#!/usr/bin/env python3
"""
Content Commands - Content management and organization

This module provides:
- List content with filtering and search
- Create new content items (lessons, exercises, assessments)
- Update existing content
- Delete content with safety checks
- Content validation and versioning
- Import/export content in various formats
- Content relationship management
"""

import json
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .base import BaseCommand, CommandResult, CommandMetadata, CommandCategory
from ..ui.formatter import TerminalFormatter
from ..models.content import Content
from ..core.exceptions import CLIError


class ContentListCommand(BaseCommand):
    """List content with filtering and search"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="content-list",
            description="List all content items with filtering",
            category=CommandCategory.CONTENT,
            aliases=["content-ls", "list-content"],
            examples=[
                "content-list",
                "content-list --type lesson",
                "content-list --curriculum 123",
                "content-list --status published --format json",
                "content-list --search 'python basics'",
                "content-list --author 'Jane Smith' --tag tutorial"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="List content items with filtering"
        )
        
        # Filtering options
        parser.add_argument(
            '--type',
            choices=['lesson', 'exercise', 'assessment', 'resource', 'video', 'quiz'],
            help='Filter by content type'
        )
        parser.add_argument(
            '--status',
            choices=['draft', 'review', 'published', 'archived'],
            help='Filter by content status'
        )
        parser.add_argument(
            '--curriculum',
            type=int,
            help='Filter by curriculum ID'
        )
        parser.add_argument(
            '--module',
            type=int,
            help='Filter by module ID'
        )
        parser.add_argument(
            '--author',
            help='Filter by author name'
        )
        parser.add_argument(
            '--tag',
            action='append',
            help='Filter by tags (can be used multiple times)'
        )
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='Filter by difficulty level'
        )
        
        # Search options
        parser.add_argument(
            '--search',
            help='Search in title and content'
        )
        parser.add_argument(
            '--search-field',
            choices=['title', 'description', 'content', 'all'],
            default='all',
            help='Fields to search in'
        )
        
        # Sorting options
        parser.add_argument(
            '--sort',
            choices=['title', 'created', 'updated', 'type', 'status', 'order'],
            default='title',
            help='Sort field'
        )
        parser.add_argument(
            '--order',
            choices=['asc', 'desc'],
            default='asc',
            help='Sort order'
        )
        
        # Output options
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'summary', 'tree'],
            default='table',
            help='Output format'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of results'
        )
        parser.add_argument(
            '--include-stats',
            action='store_true',
            help='Include content statistics'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Get content items
            content_items = await self._get_content_items(context, parsed_args)
            
            if not content_items:
                return CommandResult(
                    success=True,
                    message="No content items found matching the criteria"
                )
            
            # Format output
            if parsed_args.format == 'json':
                output = json.dumps(content_items, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_summary(context.formatter, content_items)
            elif parsed_args.format == 'tree':
                self._show_tree(context.formatter, content_items)
            else:
                self._show_table(context.formatter, content_items, parsed_args.include_stats)
            
            return CommandResult(
                success=True,
                message=f"Found {len(content_items)} content item(s)",
                data={'content_items': content_items}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to list content: {e}",
                error=e
            )
    
    async def _get_content_items(self, context, args) -> List[Dict[str, Any]]:
        """Get content items with filtering and sorting"""
        # Mock data - replace with actual database query
        mock_content = [
            {
                'id': 1,
                'title': 'Introduction to Python',
                'description': 'Learn the basics of Python programming',
                'type': 'lesson',
                'status': 'published',
                'curriculum_id': 1,
                'module_id': 1,
                'author': 'Jane Smith',
                'difficulty': 'beginner',
                'tags': ['python', 'basics', 'introduction'],
                'created': '2024-01-15T10:30:00',
                'updated': '2024-01-20T14:22:00',
                'order': 1,
                'duration': '45 minutes',
                'views': 1250,
                'completion_rate': 92.5
            },
            {
                'id': 2,
                'title': 'Python Variables Exercise',
                'description': 'Practice working with Python variables',
                'type': 'exercise',
                'status': 'published',
                'curriculum_id': 1,
                'module_id': 1,
                'author': 'Jane Smith',
                'difficulty': 'beginner',
                'tags': ['python', 'variables', 'practice'],
                'created': '2024-01-16T11:00:00',
                'updated': '2024-01-21T09:15:00',
                'order': 2,
                'duration': '30 minutes',
                'views': 980,
                'completion_rate': 87.3
            },
            {
                'id': 3,
                'title': 'Data Types Quiz',
                'description': 'Test your knowledge of Python data types',
                'type': 'quiz',
                'status': 'draft',
                'curriculum_id': 1,
                'module_id': 2,
                'author': 'John Doe',
                'difficulty': 'intermediate',
                'tags': ['python', 'data-types', 'assessment'],
                'created': '2024-01-18T15:45:00',
                'updated': '2024-01-22T10:30:00',
                'order': 1,
                'duration': '20 minutes',
                'views': 0,
                'completion_rate': 0
            }
        ]
        
        # Apply filters
        filtered_content = mock_content
        
        if args.type:
            filtered_content = [c for c in filtered_content if c['type'] == args.type]
        
        if args.status:
            filtered_content = [c for c in filtered_content if c['status'] == args.status]
        
        if args.curriculum:
            filtered_content = [c for c in filtered_content if c['curriculum_id'] == args.curriculum]
        
        if args.module:
            filtered_content = [c for c in filtered_content if c['module_id'] == args.module]
        
        if args.author:
            filtered_content = [c for c in filtered_content if args.author.lower() in c['author'].lower()]
        
        if args.difficulty:
            filtered_content = [c for c in filtered_content if c['difficulty'] == args.difficulty]
        
        if args.tag:
            for tag in args.tag:
                filtered_content = [c for c in filtered_content if tag in c['tags']]
        
        if args.search:
            search_term = args.search.lower()
            if args.search_field == 'all':
                filtered_content = [
                    c for c in filtered_content 
                    if search_term in c['title'].lower() or 
                       search_term in c['description'].lower()
                ]
            elif args.search_field == 'title':
                filtered_content = [c for c in filtered_content if search_term in c['title'].lower()]
            elif args.search_field == 'description':
                filtered_content = [c for c in filtered_content if search_term in c['description'].lower()]
        
        # Apply sorting
        reverse = args.order == 'desc'
        filtered_content.sort(key=lambda x: x.get(args.sort, ''), reverse=reverse)
        
        # Apply limit
        if args.limit:
            filtered_content = filtered_content[:args.limit]
        
        return filtered_content
    
    def _show_table(self, formatter: TerminalFormatter, content_items: List[Dict[str, Any]], include_stats: bool):
        """Show content items in table format"""
        if include_stats:
            headers = ['ID', 'Title', 'Type', 'Status', 'Views', 'Completion', 'Updated']
        else:
            headers = ['ID', 'Title', 'Type', 'Status', 'Module', 'Author']
        
        table_data = []
        for content in content_items:
            if include_stats:
                table_data.append({
                    'ID': content['id'],
                    'Title': content['title'][:25] + '...' if len(content['title']) > 25 else content['title'],
                    'Type': content['type'].upper(),
                    'Status': content['status'].upper(),
                    'Views': content.get('views', 0),
                    'Completion': f"{content.get('completion_rate', 0):.1f}%",
                    'Updated': content['updated'][:10]
                })
            else:
                table_data.append({
                    'ID': content['id'],
                    'Title': content['title'][:30] + '...' if len(content['title']) > 30 else content['title'],
                    'Type': content['type'].upper(),
                    'Status': content['status'].upper(),
                    'Module': content.get('module_id', ''),
                    'Author': content['author']
                })
        
        formatter.table(table_data, headers)
    
    def _show_summary(self, formatter: TerminalFormatter, content_items: List[Dict[str, Any]]):
        """Show content items in summary format"""
        for content in content_items:
            formatter.header(f"{content['title']} (#{content['id']})", level=3)
            
            summary = {
                'Type': content['type'].title(),
                'Status': content['status'].upper(),
                'Author': content['author'],
                'Difficulty': content['difficulty'].title(),
                'Duration': content.get('duration', 'Not specified'),
                'Tags': ', '.join(content['tags'])
            }
            
            formatter.key_value_pairs(summary, indent=1)
            formatter.info(f"  Description: {content['description']}")
            print()
    
    def _show_tree(self, formatter: TerminalFormatter, content_items: List[Dict[str, Any]]):
        """Show content items in tree format grouped by curriculum/module"""
        # Group by curriculum and module
        tree = {}
        for content in content_items:
            curr_id = content.get('curriculum_id', 'Unknown')
            mod_id = content.get('module_id', 'Unknown')
            
            if curr_id not in tree:
                tree[curr_id] = {}
            if mod_id not in tree[curr_id]:
                tree[curr_id][mod_id] = []
            
            tree[curr_id][mod_id].append(content)
        
        # Display tree
        for curr_id, modules in tree.items():
            formatter.info(f"📚 Curriculum {curr_id}")
            
            for mod_id, content_list in modules.items():
                formatter.info(f"  📖 Module {mod_id}")
                
                for content in content_list:
                    status_icon = "✅" if content['status'] == 'published' else "📝"
                    type_icon = {
                        'lesson': '📺',
                        'exercise': '💪',
                        'quiz': '❓',
                        'assessment': '📊',
                        'resource': '📄',
                        'video': '🎥'
                    }.get(content['type'], '📄')
                    
                    formatter.info(f"    {type_icon} {status_icon} {content['title']} (#{content['id']})")


class ContentCreateCommand(BaseCommand):
    """Create new content item with interactive prompts"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="content-create",
            description="Create a new content item",
            category=CommandCategory.CONTENT,
            aliases=["content-new", "create-content"],
            examples=[
                "content-create",
                "content-create --type lesson --title 'Python Basics'",
                "content-create --curriculum 123 --module 45",
                "content-create --template lesson-with-exercise",
                "content-create --from-file lesson.json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Create a new content item"
        )
        
        # Basic content information
        parser.add_argument(
            '--type',
            choices=['lesson', 'exercise', 'assessment', 'resource', 'video', 'quiz'],
            help='Content type'
        )
        parser.add_argument(
            '--title',
            help='Content title'
        )
        parser.add_argument(
            '--description',
            help='Content description'
        )
        
        # Organization
        parser.add_argument(
            '--curriculum',
            type=int,
            help='Curriculum ID'
        )
        parser.add_argument(
            '--module',
            type=int,
            help='Module ID'
        )
        parser.add_argument(
            '--order',
            type=int,
            help='Content order within module'
        )
        
        # Content properties
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='Difficulty level'
        )
        parser.add_argument(
            '--duration',
            help='Estimated duration (e.g., "30 minutes")'
        )
        parser.add_argument(
            '--tags',
            help='Comma-separated tags'
        )
        parser.add_argument(
            '--author',
            help='Author name'
        )
        
        # Creation options
        parser.add_argument(
            '--template',
            help='Use a content template'
        )
        parser.add_argument(
            '--from-file',
            help='Create from JSON file'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            default=True,
            help='Use interactive mode (default)'
        )
        parser.add_argument(
            '--no-interactive',
            action='store_true',
            help='Skip interactive prompts'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Load from file or template if specified
            if getattr(parsed_args, 'from_file', None):
                content_data = await self._load_from_file(parsed_args.from_file)
            elif parsed_args.template:
                content_data = await self._load_template(parsed_args.template)
            else:
                content_data = {}
            
            # Use interactive mode unless disabled
            if not parsed_args.no_interactive:
                content_data = await self._interactive_creation(
                    context.formatter, content_data, parsed_args
                )
            else:
                # Use command line arguments
                content_data.update(self._extract_args_data(parsed_args))
            
            # Validate required fields
            validation_errors = self._validate_content_data(content_data)
            if validation_errors:
                return CommandResult(
                    success=False,
                    message="Validation failed:\n" + "\n".join(validation_errors)
                )
            
            # Show preview and confirm
            if not parsed_args.force:
                context.formatter.header("Content Preview", level=2)
                context.formatter.key_value_pairs(content_data)
                
                if not self.confirm_action("Create this content?", default=True):
                    return CommandResult(
                        success=False,
                        message="Content creation cancelled"
                    )
            
            # Create content
            content_id = await self._create_content(context, content_data)
            
            context.formatter.success(
                f"Content '{content_data['title']}' created successfully (ID: {content_id})"
            )
            
            return CommandResult(
                success=True,
                message=f"Created content with ID {content_id}",
                data={'content_id': content_id, 'content': content_data}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to create content: {e}",
                error=e
            )
    
    async def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load content data from JSON file"""
        path = Path(file_path)
        if not path.exists():
            raise CLIError(f"File not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise CLIError(f"Invalid JSON in file {file_path}: {e}")
    
    async def _load_template(self, template_name: str) -> Dict[str, Any]:
        """Load content template"""
        templates = {
            'basic-lesson': {
                'type': 'lesson',
                'difficulty': 'beginner',
                'content_structure': {
                    'introduction': '',
                    'main_content': '',
                    'examples': [],
                    'summary': ''
                }
            },
            'interactive-exercise': {
                'type': 'exercise',
                'difficulty': 'beginner',
                'content_structure': {
                    'instructions': '',
                    'starter_code': '',
                    'solution': '',
                    'tests': []
                }
            },
            'multiple-choice-quiz': {
                'type': 'quiz',
                'difficulty': 'beginner',
                'content_structure': {
                    'questions': [],
                    'time_limit': 30,
                    'passing_score': 70
                }
            }
        }
        
        if template_name not in templates:
            raise CLIError(f"Unknown template: {template_name}. Available: {list(templates.keys())}")
        
        return templates[template_name]
    
    async def _interactive_creation(self, formatter: TerminalFormatter, 
                                   initial_data: Dict[str, Any],
                                   parsed_args) -> Dict[str, Any]:
        """Interactive content creation"""
        formatter.header("Interactive Content Creation", level=2)
        
        content_data = initial_data.copy()
        
        # Content type
        if 'type' not in content_data:
            types = ['lesson', 'exercise', 'assessment', 'resource', 'video', 'quiz']
            formatter.info("Content types:")
            for i, content_type in enumerate(types, 1):
                formatter.info(f"  {i}. {content_type.title()}")
            
            while True:
                try:
                    choice = input("Select content type (1-6): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= 6:
                        content_data['type'] = types[int(choice) - 1]
                        break
                    else:
                        formatter.warning("Please enter a number between 1 and 6")
                except ValueError:
                    formatter.warning("Please enter a valid number")
        
        # Title
        if 'title' not in content_data:
            while True:
                title = input("Content title: ").strip()
                if title:
                    content_data['title'] = title
                    break
                formatter.warning("Title is required")
        
        # Description
        if 'description' not in content_data:
            description = input("Description: ").strip()
            if description:
                content_data['description'] = description
        
        # Curriculum and module
        if 'curriculum_id' not in content_data:
            curriculum_id = input("Curriculum ID (optional): ").strip()
            if curriculum_id.isdigit():
                content_data['curriculum_id'] = int(curriculum_id)
        
        if 'module_id' not in content_data:
            module_id = input("Module ID (optional): ").strip()
            if module_id.isdigit():
                content_data['module_id'] = int(module_id)
        
        # Difficulty
        if 'difficulty' not in content_data:
            difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
            formatter.info("Difficulty levels:")
            for i, diff in enumerate(difficulties, 1):
                formatter.info(f"  {i}. {diff.title()}")
            
            while True:
                try:
                    choice = input("Select difficulty (1-4): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= 4:
                        content_data['difficulty'] = difficulties[int(choice) - 1]
                        break
                    else:
                        formatter.warning("Please enter a number between 1 and 4")
                except ValueError:
                    formatter.warning("Please enter a valid number")
        
        # Duration
        if 'duration' not in content_data:
            duration = input("Estimated duration (e.g., '30 minutes'): ").strip()
            if duration:
                content_data['duration'] = duration
        
        # Author
        if 'author' not in content_data:
            author = input("Author name: ").strip()
            if author:
                content_data['author'] = author
        
        # Tags
        if 'tags' not in content_data:
            tags_input = input("Tags (comma-separated): ").strip()
            if tags_input:
                content_data['tags'] = [tag.strip() for tag in tags_input.split(',')]
        
        # Set defaults
        content_data.setdefault('status', 'draft')
        content_data.setdefault('created', datetime.now().isoformat())
        
        return content_data
    
    def _extract_args_data(self, parsed_args) -> Dict[str, Any]:
        """Extract content data from command line arguments"""
        data = {}
        
        if parsed_args.type:
            data['type'] = parsed_args.type
        if parsed_args.title:
            data['title'] = parsed_args.title
        if parsed_args.description:
            data['description'] = parsed_args.description
        if parsed_args.curriculum:
            data['curriculum_id'] = parsed_args.curriculum
        if parsed_args.module:
            data['module_id'] = parsed_args.module
        if parsed_args.order:
            data['order'] = parsed_args.order
        if parsed_args.difficulty:
            data['difficulty'] = parsed_args.difficulty
        if parsed_args.duration:
            data['duration'] = parsed_args.duration
        if parsed_args.author:
            data['author'] = parsed_args.author
        if parsed_args.tags:
            data['tags'] = [tag.strip() for tag in parsed_args.tags.split(',')]
        
        # Set defaults
        data.setdefault('status', 'draft')
        data.setdefault('created', datetime.now().isoformat())
        
        return data
    
    def _validate_content_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate content data"""
        errors = []
        
        if not data.get('title'):
            errors.append("Title is required")
        
        if not data.get('type'):
            errors.append("Content type is required")
        elif data['type'] not in ['lesson', 'exercise', 'assessment', 'resource', 'video', 'quiz']:
            errors.append("Invalid content type")
        
        if 'difficulty' in data and data['difficulty'] not in ['beginner', 'intermediate', 'advanced', 'expert']:
            errors.append("Invalid difficulty level")
        
        if 'status' in data and data['status'] not in ['draft', 'review', 'published', 'archived']:
            errors.append("Invalid status")
        
        return errors
    
    async def _create_content(self, context, content_data: Dict[str, Any]) -> int:
        """Create the content in the database"""
        # Mock implementation - replace with actual database creation
        content_id = hash(content_data['title'] + str(datetime.now())) % 10000
        
        # In a real implementation, this would save to database
        # content = Content(**content_data)
        # await content.save()
        
        return content_id


class ContentShowCommand(BaseCommand):
    """Show detailed content information"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="content-show",
            description="Show detailed information about content",
            category=CommandCategory.CONTENT,
            aliases=["content-info", "show-content"],
            examples=[
                "content-show 123",
                "content-show 123 --format json",
                "content-show 123 --include-stats",
                "content-show 123 --include-relationships"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Show detailed content information"
        )
        
        # Identification
        parser.add_argument(
            'content_id',
            type=int,
            help='Content ID to show'
        )
        
        # Display options
        parser.add_argument(
            '--format',
            choices=['detailed', 'json', 'summary'],
            default='detailed',
            help='Output format'
        )
        parser.add_argument(
            '--include-stats',
            action='store_true',
            help='Include usage statistics'
        )
        parser.add_argument(
            '--include-relationships',
            action='store_true',
            help='Include related content'
        )
        parser.add_argument(
            '--include-content',
            action='store_true',
            help='Include actual content body'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Find content
            content = await self._find_content(context, parsed_args.content_id)
            
            if not content:
                return CommandResult(
                    success=False,
                    message=f"Content with ID {parsed_args.content_id} not found"
                )
            
            # Display content
            if parsed_args.format == 'json':
                output = json.dumps(content, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_summary(context.formatter, content)
            else:
                self._show_detailed(context.formatter, content, parsed_args)
            
            return CommandResult(
                success=True,
                data={'content': content}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to show content: {e}",
                error=e
            )
    
    async def _find_content(self, context, content_id: int) -> Optional[Dict[str, Any]]:
        """Find content by ID"""
        # Mock implementation
        if content_id == 1:
            return {
                'id': 1,
                'title': 'Introduction to Python',
                'description': 'Learn the basics of Python programming',
                'type': 'lesson',
                'status': 'published',
                'curriculum_id': 1,
                'curriculum_name': 'Python Fundamentals',
                'module_id': 1,
                'module_name': 'Getting Started',
                'author': 'Jane Smith',
                'difficulty': 'beginner',
                'tags': ['python', 'basics', 'introduction'],
                'created': '2024-01-15T10:30:00',
                'updated': '2024-01-20T14:22:00',
                'order': 1,
                'duration': '45 minutes',
                'views': 1250,
                'completion_rate': 92.5,
                'average_rating': 4.7,
                'content_body': 'This lesson introduces you to Python programming...',
                'related_content': [
                    {'id': 2, 'title': 'Python Variables Exercise', 'type': 'exercise'},
                    {'id': 3, 'title': 'Python Syntax Quiz', 'type': 'quiz'}
                ]
            }
        return None
    
    def _show_detailed(self, formatter: TerminalFormatter, content: Dict[str, Any], args):
        """Show detailed content information"""
        formatter.header(content['title'], level=1)
        
        # Basic information
        formatter.header("Basic Information", level=2)
        basic_info = {
            'ID': content['id'],
            'Type': content['type'].title(),
            'Status': content['status'].upper(),
            'Difficulty': content['difficulty'].title(),
            'Author': content['author'],
            'Duration': content.get('duration', 'Not specified'),
            'Created': content['created'],
            'Updated': content['updated']
        }
        formatter.key_value_pairs(basic_info)
        
        # Organization
        if content.get('curriculum_name') or content.get('module_name'):
            formatter.header("Organization", level=2)
            org_info = {}
            if content.get('curriculum_name'):
                org_info['Curriculum'] = f"{content['curriculum_name']} (ID: {content['curriculum_id']})"
            if content.get('module_name'):
                org_info['Module'] = f"{content['module_name']} (ID: {content['module_id']})"
            if content.get('order'):
                org_info['Order'] = content['order']
            formatter.key_value_pairs(org_info)
        
        # Description
        if content.get('description'):
            formatter.header("Description", level=2)
            formatter.info(content['description'])
        
        # Tags
        if content.get('tags'):
            formatter.header("Tags", level=2)
            formatter.list_items(content['tags'])
        
        # Statistics
        if args.include_stats:
            formatter.header("Statistics", level=2)
            stats = {
                'Views': content.get('views', 0),
                'Completion Rate': f"{content.get('completion_rate', 0):.1f}%",
                'Average Rating': f"{content.get('average_rating', 0):.1f}/5.0"
            }
            formatter.key_value_pairs(stats)
        
        # Related content
        if args.include_relationships and content.get('related_content'):
            formatter.header("Related Content", level=2)
            related_data = []
            for related in content['related_content']:
                related_data.append({
                    'ID': related['id'],
                    'Title': related['title'],
                    'Type': related['type'].upper()
                })
            formatter.table(related_data)
        
        # Content body
        if args.include_content and content.get('content_body'):
            formatter.header("Content", level=2)
            formatter.box(content['content_body'][:500] + '...' if len(content['content_body']) > 500 else content['content_body'])
    
    def _show_summary(self, formatter: TerminalFormatter, content: Dict[str, Any]):
        """Show content summary"""
        formatter.info(f"ID: {content['id']} | {content['title']}")
        formatter.info(f"Type: {content['type'].upper()} | Status: {content['status'].upper()}")
        formatter.info(f"Author: {content['author']} | Duration: {content.get('duration', 'Not specified')}")
        if content.get('views'):
            formatter.info(f"Views: {content['views']} | Completion: {content.get('completion_rate', 0):.1f}%")


class ContentUpdateCommand(BaseCommand):
    """Update existing content"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="content-update",
            description="Update an existing content item",
            category=CommandCategory.CONTENT,
            aliases=["content-edit", "update-content"],
            examples=[
                "content-update 123 --title 'New Title'",
                "content-update 123 --status published",
                "content-update 123 --difficulty intermediate",
                "content-update 123 --interactive"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Update an existing content item"
        )
        
        # Identification
        parser.add_argument(
            'content_id',
            type=int,
            help='Content ID to update'
        )
        
        # Update fields
        parser.add_argument(
            '--title',
            help='New title'
        )
        parser.add_argument(
            '--description',
            help='New description'
        )
        parser.add_argument(
            '--status',
            choices=['draft', 'review', 'published', 'archived'],
            help='New status'
        )
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='New difficulty level'
        )
        parser.add_argument(
            '--duration',
            help='New duration estimate'
        )
        parser.add_argument(
            '--tags',
            help='New tags (comma-separated)'
        )
        parser.add_argument(
            '--author',
            help='New author'
        )
        parser.add_argument(
            '--order',
            type=int,
            help='New order position'
        )
        
        # Options
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Use interactive mode'
        )
        parser.add_argument(
            '--show-diff',
            action='store_true',
            help='Show changes before applying'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Find content
            content = await self._find_content(context, parsed_args.content_id)
            if not content:
                return CommandResult(
                    success=False,
                    message=f"Content with ID {parsed_args.content_id} not found"
                )
            
            original_content = content.copy()
            
            # Get updates
            if parsed_args.interactive:
                updates = await self._interactive_update(context.formatter, content)
            else:
                updates = self._extract_updates(parsed_args)
            
            if not updates:
                return CommandResult(
                    success=False,
                    message="No updates specified"
                )
            
            # Apply updates
            updated_content = content.copy()
            updated_content.update(updates)
            updated_content['updated'] = datetime.now().isoformat()
            
            # Show diff if requested
            if parsed_args.show_diff:
                self._show_diff(context.formatter, original_content, updated_content)
            
            # Confirm update
            if not parsed_args.force:
                if not self.confirm_action(
                    f"Update content '{content['title']}'?", 
                    default=True
                ):
                    return CommandResult(
                        success=False,
                        message="Update cancelled"
                    )
            
            # Perform update
            await self._update_content(context, parsed_args.content_id, updated_content)
            
            context.formatter.success(
                f"Content '{content['title']}' updated successfully"
            )
            
            return CommandResult(
                success=True,
                message="Content updated successfully",
                data={'content': updated_content, 'updates': updates}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to update content: {e}",
                error=e
            )
    
    async def _find_content(self, context, content_id: int) -> Optional[Dict[str, Any]]:
        """Find content by ID"""
        # Mock implementation
        if content_id == 1:
            return {
                'id': 1,
                'title': 'Introduction to Python',
                'description': 'Learn the basics of Python programming',
                'type': 'lesson',
                'status': 'published',
                'difficulty': 'beginner',
                'duration': '45 minutes',
                'author': 'Jane Smith',
                'tags': ['python', 'basics', 'introduction'],
                'order': 1,
                'created': '2024-01-15T10:30:00',
                'updated': '2024-01-20T14:22:00'
            }
        return None
    
    def _extract_updates(self, parsed_args) -> Dict[str, Any]:
        """Extract updates from command line arguments"""
        updates = {}
        
        if parsed_args.title:
            updates['title'] = parsed_args.title
        if parsed_args.description:
            updates['description'] = parsed_args.description
        if parsed_args.status:
            updates['status'] = parsed_args.status
        if parsed_args.difficulty:
            updates['difficulty'] = parsed_args.difficulty
        if parsed_args.duration:
            updates['duration'] = parsed_args.duration
        if parsed_args.author:
            updates['author'] = parsed_args.author
        if parsed_args.order is not None:
            updates['order'] = parsed_args.order
        if parsed_args.tags:
            updates['tags'] = [tag.strip() for tag in parsed_args.tags.split(',')]
        
        return updates
    
    async def _interactive_update(self, formatter: TerminalFormatter, 
                                 content: Dict[str, Any]) -> Dict[str, Any]:
        """Interactive content update"""
        formatter.header(f"Updating Content: {content['title']}", level=2)
        formatter.info("Press Enter to keep current value, or enter new value:")
        
        updates = {}
        
        # Title
        current_title = content.get('title', '')
        new_title = input(f"Title [{current_title}]: ").strip()
        if new_title and new_title != current_title:
            updates['title'] = new_title
        
        # Description
        current_desc = content.get('description', '')
        new_desc = input(f"Description [{current_desc[:30]}{'...' if len(current_desc) > 30 else ''}]: ").strip()
        if new_desc and new_desc != current_desc:
            updates['description'] = new_desc
        
        # Status
        current_status = content.get('status', '')
        statuses = ['draft', 'review', 'published', 'archived']
        formatter.info(f"Status options: {', '.join(statuses)}")
        new_status = input(f"Status [{current_status}]: ").strip()
        if new_status and new_status != current_status and new_status in statuses:
            updates['status'] = new_status
        
        # Difficulty
        current_difficulty = content.get('difficulty', '')
        difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        formatter.info(f"Difficulty options: {', '.join(difficulties)}")
        new_difficulty = input(f"Difficulty [{current_difficulty}]: ").strip()
        if new_difficulty and new_difficulty != current_difficulty and new_difficulty in difficulties:
            updates['difficulty'] = new_difficulty
        
        # Duration
        current_duration = content.get('duration', '')
        new_duration = input(f"Duration [{current_duration}]: ").strip()
        if new_duration and new_duration != current_duration:
            updates['duration'] = new_duration
        
        # Tags
        current_tags = ', '.join(content.get('tags', []))
        new_tags = input(f"Tags [{current_tags}]: ").strip()
        if new_tags and new_tags != current_tags:
            updates['tags'] = [tag.strip() for tag in new_tags.split(',')]
        
        return updates
    
    def _show_diff(self, formatter: TerminalFormatter, 
                   original: Dict[str, Any], 
                   updated: Dict[str, Any]):
        """Show differences between original and updated content"""
        formatter.header("Changes Preview", level=2)
        
        changes = []
        for key, new_value in updated.items():
            if key in original and original[key] != new_value:
                changes.append({
                    'Field': key.title(),
                    'Before': str(original[key]),
                    'After': str(new_value)
                })
        
        if changes:
            formatter.table(changes)
        else:
            formatter.info("No changes detected")
    
    async def _update_content(self, context, content_id: int, 
                             updated_content: Dict[str, Any]):
        """Update content in database"""
        # Mock implementation - replace with actual database update
        pass


class ContentDeleteCommand(BaseCommand):
    """Delete content with confirmation"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="content-delete",
            description="Delete content with confirmation",
            category=CommandCategory.CONTENT,
            aliases=["content-remove", "delete-content"],
            examples=[
                "content-delete 123",
                "content-delete 123 --force",
                "content-delete 123 --backup"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Delete a content item"
        )
        
        # Identification
        parser.add_argument(
            'content_id',
            type=int,
            help='Content ID to delete'
        )
        
        # Safety options
        parser.add_argument(
            '--backup',
            action='store_true',
            default=True,
            help='Create backup before deletion (default)'
        )
        parser.add_argument(
            '--no-backup',
            action='store_true',
            help='Skip backup creation'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Find content
            content = await self._find_content(context, parsed_args.content_id)
            if not content:
                return CommandResult(
                    success=False,
                    message=f"Content with ID {parsed_args.content_id} not found"
                )
            
            # Show content info
            context.formatter.warning("About to delete content:")
            summary = {
                'ID': content['id'],
                'Title': content['title'],
                'Type': content['type'].upper(),
                'Status': content['status'].upper(),
                'Views': content.get('views', 0)
            }
            context.formatter.key_value_pairs(summary)
            
            # Confirm deletion
            if not parsed_args.force:
                if not self.confirm_action(
                    f"This will permanently delete content '{content['title']}'. Are you sure?", 
                    default=False
                ):
                    return CommandResult(
                        success=False,
                        message="Deletion cancelled"
                    )
            
            # Create backup if requested
            backup_path = None
            if not parsed_args.no_backup:
                backup_path = await self._create_backup(context, content)
                context.formatter.info(f"Backup created: {backup_path}")
            
            # Perform deletion
            await self._delete_content(context, content['id'])
            
            context.formatter.success(
                f"Content '{content['title']}' deleted successfully"
            )
            
            return CommandResult(
                success=True,
                message="Content deleted successfully",
                data={'deleted_content_id': content['id'], 'backup_path': backup_path}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to delete content: {e}",
                error=e
            )
    
    async def _find_content(self, context, content_id: int) -> Optional[Dict[str, Any]]:
        """Find content by ID"""
        # Mock implementation
        if content_id == 1:
            return {
                'id': 1,
                'title': 'Introduction to Python',
                'type': 'lesson',
                'status': 'published',
                'views': 1250
            }
        return None
    
    async def _create_backup(self, context, content: Dict[str, Any]) -> str:
        """Create backup of content data"""
        # Mock implementation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"content_{content['id']}_{timestamp}.json"
        backup_path = Path("backups") / backup_filename
        
        # In real implementation, save content data to backup file
        backup_path.parent.mkdir(exist_ok=True)
        with open(backup_path, 'w') as f:
            json.dump(content, f, indent=2, default=str)
        
        return str(backup_path)
    
    async def _delete_content(self, context, content_id: int):
        """Delete content from database"""
        # Mock implementation - replace with actual database deletion
        pass
