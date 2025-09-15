#!/usr/bin/env python3
"""
Curriculum Commands - CRUD operations for curriculum management

This module provides:
- List all curricula with filtering and sorting
- Create new curriculum with interactive prompts
- Update existing curriculum details
- Delete curriculum with confirmation
- Show detailed curriculum information
- Export/import curriculum data
- Curriculum validation and status management
"""

import json
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .base import BaseCommand, CommandResult, CommandMetadata, CommandCategory
from ..ui.formatter import TerminalFormatter
from ..ui.interactive import InteractiveSession
from ..models.curriculum import Curriculum
from ..core.exceptions import CLIError


class CurriculumListCommand(BaseCommand):
    """List all curricula with filtering and sorting options"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="curriculum-list",
            description="List all curricula with filtering and sorting",
            category=CommandCategory.CURRICULUM,
            aliases=["curr-list", "list-curr"],
            examples=[
                "curriculum-list",
                "curriculum-list --status active",
                "curriculum-list --format json",
                "curriculum-list --sort name --order desc",
                "curriculum-list --tag python --difficulty beginner"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="List all curricula with optional filtering"
        )
        
        # Filtering options
        parser.add_argument(
            '--status', 
            choices=['active', 'draft', 'archived', 'published'],
            help='Filter by curriculum status'
        )
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='Filter by difficulty level'
        )
        parser.add_argument(
            '--tag',
            action='append',
            help='Filter by tags (can be used multiple times)'
        )
        parser.add_argument(
            '--author',
            help='Filter by author name'
        )
        parser.add_argument(
            '--category',
            help='Filter by category'
        )
        
        # Sorting options
        parser.add_argument(
            '--sort',
            choices=['name', 'created', 'updated', 'difficulty', 'status'],
            default='name',
            help='Sort field (default: name)'
        )
        parser.add_argument(
            '--order',
            choices=['asc', 'desc'],
            default='asc',
            help='Sort order (default: asc)'
        )
        
        # Output options
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'summary'],
            default='table',
            help='Output format (default: table)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of results'
        )
        parser.add_argument(
            '--search',
            help='Search in curriculum names and descriptions'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Mock data for demonstration - replace with actual database queries
            curricula = await self._get_curricula(context, parsed_args)
            
            if not curricula:
                return CommandResult(
                    success=True,
                    message="No curricula found matching the criteria"
                )
            
            # Format output
            if parsed_args.format == 'json':
                output = json.dumps(curricula, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_summary(context.formatter, curricula)
            else:
                self._show_table(context.formatter, curricula)
            
            return CommandResult(
                success=True,
                message=f"Found {len(curricula)} curriculum(s)",
                data={'curricula': curricula}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to list curricula: {e}",
                error=e
            )
    
    async def _get_curricula(self, context, args) -> List[Dict[str, Any]]:
        """Get curricula with filtering and sorting"""
        # Mock data - replace with actual database query
        mock_curricula = [
            {
                'id': 1,
                'name': 'Python Fundamentals',
                'description': 'Learn Python programming from basics to advanced',
                'status': 'active',
                'difficulty': 'beginner',
                'category': 'Programming',
                'author': 'Jane Smith',
                'tags': ['python', 'programming', 'fundamentals'],
                'created': '2024-01-15',
                'updated': '2024-02-01',
                'modules': 12,
                'students': 245
            },
            {
                'id': 2,
                'name': 'Data Structures & Algorithms',
                'description': 'Master computer science fundamentals',
                'status': 'active',
                'difficulty': 'intermediate',
                'category': 'Computer Science',
                'author': 'John Doe',
                'tags': ['algorithms', 'data-structures', 'computer-science'],
                'created': '2024-01-10',
                'updated': '2024-01-25',
                'modules': 18,
                'students': 189
            },
            {
                'id': 3,
                'name': 'Machine Learning Basics',
                'description': 'Introduction to ML concepts and implementations',
                'status': 'draft',
                'difficulty': 'advanced',
                'category': 'AI/ML',
                'author': 'Alice Johnson',
                'tags': ['machine-learning', 'ai', 'python'],
                'created': '2024-02-01',
                'updated': '2024-02-10',
                'modules': 8,
                'students': 0
            }
        ]
        
        # Apply filters
        filtered_curricula = mock_curricula
        
        if args.status:
            filtered_curricula = [c for c in filtered_curricula if c['status'] == args.status]
        
        if args.difficulty:
            filtered_curricula = [c for c in filtered_curricula if c['difficulty'] == args.difficulty]
        
        if args.tag:
            for tag in args.tag:
                filtered_curricula = [c for c in filtered_curricula if tag in c['tags']]
        
        if args.author:
            filtered_curricula = [c for c in filtered_curricula if args.author.lower() in c['author'].lower()]
        
        if args.category:
            filtered_curricula = [c for c in filtered_curricula if args.category.lower() in c['category'].lower()]
        
        if args.search:
            search_term = args.search.lower()
            filtered_curricula = [
                c for c in filtered_curricula 
                if search_term in c['name'].lower() or search_term in c['description'].lower()
            ]
        
        # Apply sorting
        reverse = args.order == 'desc'
        filtered_curricula.sort(key=lambda x: x.get(args.sort, ''), reverse=reverse)
        
        # Apply limit
        if args.limit:
            filtered_curricula = filtered_curricula[:args.limit]
        
        return filtered_curricula
    
    def _show_table(self, formatter: TerminalFormatter, curricula: List[Dict[str, Any]]):
        """Show curricula in table format"""
        headers = ['ID', 'Name', 'Status', 'Difficulty', 'Category', 'Modules', 'Students']
        
        table_data = []
        for curriculum in curricula:
            table_data.append({
                'ID': curriculum['id'],
                'Name': curriculum['name'][:30] + '...' if len(curriculum['name']) > 30 else curriculum['name'],
                'Status': curriculum['status'].upper(),
                'Difficulty': curriculum['difficulty'].title(),
                'Category': curriculum['category'],
                'Modules': curriculum['modules'],
                'Students': curriculum['students']
            })
        
        formatter.table(table_data, headers)
    
    def _show_summary(self, formatter: TerminalFormatter, curricula: List[Dict[str, Any]]):
        """Show curricula in summary format"""
        for curriculum in curricula:
            formatter.header(curriculum['name'], level=3)
            
            details = {
                'Status': curriculum['status'].upper(),
                'Difficulty': curriculum['difficulty'].title(),
                'Category': curriculum['category'],
                'Author': curriculum['author'],
                'Modules': curriculum['modules'],
                'Students': curriculum['students'],
                'Tags': ', '.join(curriculum['tags'])
            }
            
            formatter.key_value_pairs(details, indent=1)
            formatter.info(f"  Description: {curriculum['description']}")
            print()


class CurriculumCreateCommand(BaseCommand):
    """Create new curriculum with interactive prompts"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="curriculum-create",
            description="Create a new curriculum interactively",
            category=CommandCategory.CURRICULUM,
            aliases=["curr-create", "create-curr"],
            examples=[
                "curriculum-create",
                "curriculum-create --name 'Advanced Python' --difficulty advanced",
                "curriculum-create --template basic-programming",
                "curriculum-create --from-file curriculum.json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Create a new curriculum"
        )
        
        # Direct creation options
        parser.add_argument(
            '--name',
            help='Curriculum name'
        )
        parser.add_argument(
            '--description',
            help='Curriculum description'
        )
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='Difficulty level'
        )
        parser.add_argument(
            '--category',
            help='Curriculum category'
        )
        parser.add_argument(
            '--tags',
            help='Comma-separated tags'
        )
        parser.add_argument(
            '--author',
            help='Author name'
        )
        
        # Template and import options
        parser.add_argument(
            '--template',
            help='Use a template for creation'
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
            
            # Load from file if specified
            if getattr(parsed_args, 'from_file', None):
                curriculum_data = await self._load_from_file(parsed_args.from_file)
            elif parsed_args.template:
                curriculum_data = await self._load_template(parsed_args.template)
            else:
                curriculum_data = {}
            
            # Use interactive mode unless disabled
            if not parsed_args.no_interactive:
                curriculum_data = await self._interactive_creation(
                    context.formatter, curriculum_data, parsed_args
                )
            else:
                # Use command line arguments
                curriculum_data.update(self._extract_args_data(parsed_args))
            
            # Validate required fields
            validation_errors = self._validate_curriculum_data(curriculum_data)
            if validation_errors:
                return CommandResult(
                    success=False,
                    message="Validation failed:\n" + "\n".join(validation_errors)
                )
            
            # Show preview and confirm
            if not parsed_args.force:
                context.formatter.header("Curriculum Preview", level=2)
                context.formatter.key_value_pairs(curriculum_data)
                
                if not self.confirm_action("Create this curriculum?", default=True):
                    return CommandResult(
                        success=False,
                        message="Curriculum creation cancelled"
                    )
            
            # Create curriculum
            curriculum_id = await self._create_curriculum(context, curriculum_data)
            
            context.formatter.success(
                f"Curriculum '{curriculum_data['name']}' created successfully (ID: {curriculum_id})"
            )
            
            return CommandResult(
                success=True,
                message=f"Created curriculum with ID {curriculum_id}",
                data={'curriculum_id': curriculum_id, 'curriculum': curriculum_data}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to create curriculum: {e}",
                error=e
            )
    
    async def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load curriculum data from JSON file"""
        path = Path(file_path)
        if not path.exists():
            raise CLIError(f"File not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise CLIError(f"Invalid JSON in file {file_path}: {e}")
    
    async def _load_template(self, template_name: str) -> Dict[str, Any]:
        """Load curriculum template"""
        templates = {
            'basic-programming': {
                'category': 'Programming',
                'difficulty': 'beginner',
                'tags': ['programming', 'fundamentals'],
                'modules': []
            },
            'data-science': {
                'category': 'Data Science',
                'difficulty': 'intermediate',
                'tags': ['data-science', 'python', 'statistics'],
                'modules': []
            },
            'web-development': {
                'category': 'Web Development',
                'difficulty': 'beginner',
                'tags': ['web', 'html', 'css', 'javascript'],
                'modules': []
            }
        }
        
        if template_name not in templates:
            raise CLIError(f"Unknown template: {template_name}. Available: {list(templates.keys())}")
        
        return templates[template_name]
    
    async def _interactive_creation(self, formatter: TerminalFormatter, 
                                   initial_data: Dict[str, Any],
                                   parsed_args) -> Dict[str, Any]:
        """Interactive curriculum creation"""
        formatter.header("Interactive Curriculum Creation", level=2)
        
        curriculum_data = initial_data.copy()
        
        # Get basic information
        if 'name' not in curriculum_data:
            while True:
                name = input("Curriculum name: ").strip()
                if name:
                    curriculum_data['name'] = name
                    break
                formatter.warning("Name is required")
        
        if 'description' not in curriculum_data:
            description = input(f"Description (optional): ").strip()
            if description:
                curriculum_data['description'] = description
        
        # Get difficulty level
        if 'difficulty' not in curriculum_data:
            difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
            formatter.info("Available difficulty levels:")
            for i, diff in enumerate(difficulties, 1):
                formatter.info(f"  {i}. {diff.title()}")
            
            while True:
                try:
                    choice = input("Select difficulty (1-4): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= 4:
                        curriculum_data['difficulty'] = difficulties[int(choice) - 1]
                        break
                    else:
                        formatter.warning("Please enter a number between 1 and 4")
                except ValueError:
                    formatter.warning("Please enter a valid number")
        
        # Get category
        if 'category' not in curriculum_data:
            category = input("Category (e.g., Programming, Data Science): ").strip()
            if category:
                curriculum_data['category'] = category
        
        # Get author
        if 'author' not in curriculum_data:
            author = input("Author name: ").strip()
            if author:
                curriculum_data['author'] = author
        
        # Get tags
        if 'tags' not in curriculum_data:
            tags_input = input("Tags (comma-separated): ").strip()
            if tags_input:
                curriculum_data['tags'] = [tag.strip() for tag in tags_input.split(',')]
        
        # Set defaults
        curriculum_data.setdefault('status', 'draft')
        curriculum_data.setdefault('created', datetime.now().isoformat())
        curriculum_data.setdefault('modules', [])
        
        return curriculum_data
    
    def _extract_args_data(self, parsed_args) -> Dict[str, Any]:
        """Extract curriculum data from command line arguments"""
        data = {}
        
        if parsed_args.name:
            data['name'] = parsed_args.name
        if parsed_args.description:
            data['description'] = parsed_args.description
        if parsed_args.difficulty:
            data['difficulty'] = parsed_args.difficulty
        if parsed_args.category:
            data['category'] = parsed_args.category
        if parsed_args.author:
            data['author'] = parsed_args.author
        if parsed_args.tags:
            data['tags'] = [tag.strip() for tag in parsed_args.tags.split(',')]
        
        # Set defaults
        data.setdefault('status', 'draft')
        data.setdefault('created', datetime.now().isoformat())
        data.setdefault('modules', [])
        
        return data
    
    def _validate_curriculum_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate curriculum data"""
        errors = []
        
        if not data.get('name'):
            errors.append("Name is required")
        
        if 'difficulty' in data and data['difficulty'] not in ['beginner', 'intermediate', 'advanced', 'expert']:
            errors.append("Invalid difficulty level")
        
        if 'status' in data and data['status'] not in ['draft', 'active', 'archived', 'published']:
            errors.append("Invalid status")
        
        return errors
    
    async def _create_curriculum(self, context, curriculum_data: Dict[str, Any]) -> int:
        """Create the curriculum in the database"""
        # Mock implementation - replace with actual database creation
        curriculum_id = hash(curriculum_data['name'] + str(datetime.now())) % 10000
        
        # In a real implementation, this would save to database
        # curriculum = Curriculum(**curriculum_data)
        # await curriculum.save()
        
        return curriculum_id


class CurriculumShowCommand(BaseCommand):
    """Show detailed curriculum information"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="curriculum-show",
            description="Show detailed information about a curriculum",
            category=CommandCategory.CURRICULUM,
            aliases=["curr-show", "show-curr"],
            examples=[
                "curriculum-show 123",
                "curriculum-show --name 'Python Fundamentals'",
                "curriculum-show 123 --format json",
                "curriculum-show 123 --include-modules"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Show detailed curriculum information"
        )
        
        # Identification
        parser.add_argument(
            'identifier',
            nargs='?',
            help='Curriculum ID or name'
        )
        parser.add_argument(
            '--name',
            help='Find curriculum by name'
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Find curriculum by ID'
        )
        
        # Display options
        parser.add_argument(
            '--format',
            choices=['detailed', 'json', 'summary'],
            default='detailed',
            help='Output format'
        )
        parser.add_argument(
            '--include-modules',
            action='store_true',
            help='Include module details'
        )
        parser.add_argument(
            '--include-stats',
            action='store_true',
            help='Include statistics'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Determine curriculum identifier
            curriculum_id = None
            curriculum_name = None
            
            if parsed_args.identifier:
                if parsed_args.identifier.isdigit():
                    curriculum_id = int(parsed_args.identifier)
                else:
                    curriculum_name = parsed_args.identifier
            elif parsed_args.id:
                curriculum_id = parsed_args.id
            elif parsed_args.name:
                curriculum_name = parsed_args.name
            else:
                return CommandResult(
                    success=False,
                    message="Please specify curriculum ID or name"
                )
            
            # Find curriculum
            curriculum = await self._find_curriculum(context, curriculum_id, curriculum_name)
            
            if not curriculum:
                return CommandResult(
                    success=False,
                    message="Curriculum not found"
                )
            
            # Display curriculum
            if parsed_args.format == 'json':
                output = json.dumps(curriculum, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_summary(context.formatter, curriculum)
            else:
                self._show_detailed(context.formatter, curriculum, parsed_args)
            
            return CommandResult(
                success=True,
                data={'curriculum': curriculum}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to show curriculum: {e}",
                error=e
            )
    
    async def _find_curriculum(self, context, curriculum_id: Optional[int], 
                              curriculum_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find curriculum by ID or name"""
        # Mock data - replace with actual database query
        curricula = [
            {
                'id': 1,
                'name': 'Python Fundamentals',
                'description': 'Learn Python programming from basics to advanced concepts',
                'status': 'active',
                'difficulty': 'beginner',
                'category': 'Programming',
                'author': 'Jane Smith',
                'tags': ['python', 'programming', 'fundamentals'],
                'created': '2024-01-15T10:30:00',
                'updated': '2024-02-01T14:22:00',
                'modules': [
                    {'id': 1, 'name': 'Introduction to Python', 'order': 1, 'status': 'published'},
                    {'id': 2, 'name': 'Variables and Data Types', 'order': 2, 'status': 'published'},
                    {'id': 3, 'name': 'Control Structures', 'order': 3, 'status': 'draft'}
                ],
                'students': 245,
                'completion_rate': 78.5,
                'average_rating': 4.6,
                'total_duration': '120 hours'
            }
        ]
        
        for curriculum in curricula:
            if curriculum_id and curriculum['id'] == curriculum_id:
                return curriculum
            elif curriculum_name and curriculum_name.lower() in curriculum['name'].lower():
                return curriculum
        
        return None
    
    def _show_detailed(self, formatter: TerminalFormatter, curriculum: Dict[str, Any], args):
        """Show detailed curriculum information with enhanced formatting"""
        # Use banner style for main title
        formatter.header(curriculum['name'], level=1, style="banner", 
                        subtitle=f"{curriculum['category']} | {curriculum['difficulty'].title()}")
        
        # Use a decorative frame for the description
        formatter.box(
            curriculum['description'],
            title="📚 What You'll Learn",
            style="double",
            padding=2,
            color=formatter.theme.primary if hasattr(formatter, 'theme') else None
        )
        
        # Basic information in a panel
        basic_info_content = []
        basic_info_content.append(f"Status: {curriculum['status'].upper()}")
        basic_info_content.append(f"Author: {curriculum['author']}")
        basic_info_content.append(f"Created: {curriculum['created']}")
        basic_info_content.append(f"Updated: {curriculum['updated']}")
        
        sections = [("📊 Course Details", "\n".join(basic_info_content))]
        
        # Add tags if present
        if curriculum.get('tags'):
            tags_content = " • ".join([f"#{tag}" for tag in curriculum['tags']])
            sections.append(("🏷️ Topics Covered", tags_content))
        
        # Add statistics if requested
        if args.include_stats and 'students' in curriculum:
            stats_lines = []
            stats_lines.append(f"👥 Students Enrolled: {curriculum.get('students', 0)}")
            stats_lines.append(f"✅ Completion Rate: {curriculum.get('completion_rate', 0)}%")
            stats_lines.append(f"⭐ Average Rating: {curriculum.get('average_rating', 0)}/5.0")
            stats_lines.append(f"⏱️ Total Duration: {curriculum.get('total_duration', 'Not specified')}")
            sections.append(("📈 Performance Metrics", "\n".join(stats_lines)))
        
        # Display all sections in a panel
        formatter.panel(sections, title="CURRICULUM OVERVIEW")
        
        # Modules with enhanced formatting
        if args.include_modules and curriculum.get('modules'):
            formatter.header("📚 Course Modules", level=2)
            
            for i, module in enumerate(curriculum['modules'], 1):
                status_icon = "✅" if module['status'] == 'published' else "🔄" if module['status'] == 'draft' else "⏸️"
                module_line = f"  {i}. {status_icon} {module['name']}"
                
                if module['status'] == 'published':
                    formatter.success(module_line)
                elif module['status'] == 'draft':
                    formatter.warning(module_line)
                else:
                    formatter.info(module_line)
            
            # Add a progress visualization
            published_count = sum(1 for m in curriculum['modules'] if m['status'] == 'published')
            total_count = len(curriculum['modules'])
            progress_pct = (published_count / total_count * 100) if total_count > 0 else 0
            
            progress_bar = formatter.progress_with_eta(
                current=published_count,
                total=total_count,
                description="Module Completion"
            )
            print(f"\n{progress_bar}")
    
    def _show_summary(self, formatter: TerminalFormatter, curriculum: Dict[str, Any]):
        """Show curriculum summary"""
        formatter.info(f"ID: {curriculum['id']} | {curriculum['name']}")
        formatter.info(f"Status: {curriculum['status'].upper()} | Difficulty: {curriculum['difficulty'].title()}")
        formatter.info(f"Category: {curriculum['category']} | Author: {curriculum['author']}")
        if curriculum.get('students'):
            formatter.info(f"Students: {curriculum['students']} | Modules: {len(curriculum.get('modules', []))}")


class CurriculumUpdateCommand(BaseCommand):
    """Update existing curriculum"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="curriculum-update",
            description="Update an existing curriculum",
            category=CommandCategory.CURRICULUM,
            aliases=["curr-update", "update-curr"],
            examples=[
                "curriculum-update 123 --name 'New Name'",
                "curriculum-update 123 --status published",
                "curriculum-update 123 --difficulty advanced",
                "curriculum-update 123 --interactive"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Update an existing curriculum"
        )
        
        # Identification
        parser.add_argument(
            'curriculum_id',
            type=int,
            help='Curriculum ID to update'
        )
        
        # Update fields
        parser.add_argument(
            '--name',
            help='New curriculum name'
        )
        parser.add_argument(
            '--description',
            help='New description'
        )
        parser.add_argument(
            '--status',
            choices=['draft', 'active', 'archived', 'published'],
            help='New status'
        )
        parser.add_argument(
            '--difficulty',
            choices=['beginner', 'intermediate', 'advanced', 'expert'],
            help='New difficulty level'
        )
        parser.add_argument(
            '--category',
            help='New category'
        )
        parser.add_argument(
            '--author',
            help='New author'
        )
        parser.add_argument(
            '--tags',
            help='New tags (comma-separated)'
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
            
            # Find curriculum
            curriculum = await self._find_curriculum(context, parsed_args.curriculum_id)
            if not curriculum:
                return CommandResult(
                    success=False,
                    message=f"Curriculum with ID {parsed_args.curriculum_id} not found"
                )
            
            original_curriculum = curriculum.copy()
            
            # Get updates
            if parsed_args.interactive:
                updates = await self._interactive_update(context.formatter, curriculum)
            else:
                updates = self._extract_updates(parsed_args)
            
            if not updates:
                return CommandResult(
                    success=False,
                    message="No updates specified"
                )
            
            # Apply updates
            updated_curriculum = curriculum.copy()
            updated_curriculum.update(updates)
            updated_curriculum['updated'] = datetime.now().isoformat()
            
            # Show diff if requested
            if parsed_args.show_diff:
                self._show_diff(context.formatter, original_curriculum, updated_curriculum)
            
            # Confirm update
            if not parsed_args.force:
                if not self.confirm_action(
                    f"Update curriculum '{curriculum['name']}'?", 
                    default=True
                ):
                    return CommandResult(
                        success=False,
                        message="Update cancelled"
                    )
            
            # Perform update
            await self._update_curriculum(context, parsed_args.curriculum_id, updated_curriculum)
            
            context.formatter.success(
                f"Curriculum '{curriculum['name']}' updated successfully"
            )
            
            return CommandResult(
                success=True,
                message="Curriculum updated successfully",
                data={'curriculum': updated_curriculum, 'updates': updates}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to update curriculum: {e}",
                error=e
            )
    
    async def _find_curriculum(self, context, curriculum_id: int) -> Optional[Dict[str, Any]]:
        """Find curriculum by ID"""
        # Mock implementation
        if curriculum_id == 1:
            return {
                'id': 1,
                'name': 'Python Fundamentals',
                'description': 'Learn Python programming from basics to advanced',
                'status': 'active',
                'difficulty': 'beginner',
                'category': 'Programming',
                'author': 'Jane Smith',
                'tags': ['python', 'programming', 'fundamentals'],
                'created': '2024-01-15T10:30:00',
                'updated': '2024-02-01T14:22:00'
            }
        return None
    
    def _extract_updates(self, parsed_args) -> Dict[str, Any]:
        """Extract updates from command line arguments"""
        updates = {}
        
        if parsed_args.name:
            updates['name'] = parsed_args.name
        if parsed_args.description:
            updates['description'] = parsed_args.description
        if parsed_args.status:
            updates['status'] = parsed_args.status
        if parsed_args.difficulty:
            updates['difficulty'] = parsed_args.difficulty
        if parsed_args.category:
            updates['category'] = parsed_args.category
        if parsed_args.author:
            updates['author'] = parsed_args.author
        if parsed_args.tags:
            updates['tags'] = [tag.strip() for tag in parsed_args.tags.split(',')]
        
        return updates
    
    async def _interactive_update(self, formatter: TerminalFormatter, 
                                 curriculum: Dict[str, Any]) -> Dict[str, Any]:
        """Interactive curriculum update"""
        formatter.header(f"Updating Curriculum: {curriculum['name']}", level=2)
        formatter.info("Press Enter to keep current value, or enter new value:")
        
        updates = {}
        
        # Name
        current_name = curriculum.get('name', '')
        new_name = input(f"Name [{current_name}]: ").strip()
        if new_name and new_name != current_name:
            updates['name'] = new_name
        
        # Description
        current_desc = curriculum.get('description', '')
        new_desc = input(f"Description [{current_desc[:50]}{'...' if len(current_desc) > 50 else ''}]: ").strip()
        if new_desc and new_desc != current_desc:
            updates['description'] = new_desc
        
        # Status
        current_status = curriculum.get('status', '')
        statuses = ['draft', 'active', 'archived', 'published']
        formatter.info(f"Status options: {', '.join(statuses)}")
        new_status = input(f"Status [{current_status}]: ").strip()
        if new_status and new_status != current_status and new_status in statuses:
            updates['status'] = new_status
        
        # Difficulty
        current_difficulty = curriculum.get('difficulty', '')
        difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        formatter.info(f"Difficulty options: {', '.join(difficulties)}")
        new_difficulty = input(f"Difficulty [{current_difficulty}]: ").strip()
        if new_difficulty and new_difficulty != current_difficulty and new_difficulty in difficulties:
            updates['difficulty'] = new_difficulty
        
        # Category
        current_category = curriculum.get('category', '')
        new_category = input(f"Category [{current_category}]: ").strip()
        if new_category and new_category != current_category:
            updates['category'] = new_category
        
        # Tags
        current_tags = ', '.join(curriculum.get('tags', []))
        new_tags = input(f"Tags [{current_tags}]: ").strip()
        if new_tags and new_tags != current_tags:
            updates['tags'] = [tag.strip() for tag in new_tags.split(',')]
        
        return updates
    
    def _show_diff(self, formatter: TerminalFormatter, 
                   original: Dict[str, Any], 
                   updated: Dict[str, Any]):
        """Show differences between original and updated curriculum"""
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
    
    async def _update_curriculum(self, context, curriculum_id: int, 
                                updated_curriculum: Dict[str, Any]):
        """Update curriculum in database"""
        # Mock implementation - replace with actual database update
        pass


class CurriculumDeleteCommand(BaseCommand):
    """Delete curriculum with confirmation"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="curriculum-delete",
            description="Delete a curriculum with confirmation",
            category=CommandCategory.CURRICULUM,
            aliases=["curr-delete", "delete-curr"],
            examples=[
                "curriculum-delete 123",
                "curriculum-delete 123 --force",
                "curriculum-delete --name 'Old Curriculum'"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Delete a curriculum"
        )
        
        # Identification
        parser.add_argument(
            'curriculum_id',
            nargs='?',
            type=int,
            help='Curriculum ID to delete'
        )
        parser.add_argument(
            '--name',
            help='Find curriculum by name to delete'
        )
        
        # Safety options
        parser.add_argument(
            '--cascade',
            action='store_true',
            help='Also delete associated modules and content'
        )
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
            
            # Find curriculum
            curriculum_id = parsed_args.curriculum_id
            curriculum_name = parsed_args.name
            
            if not curriculum_id and not curriculum_name:
                return CommandResult(
                    success=False,
                    message="Please specify curriculum ID or name to delete"
                )
            
            curriculum = await self._find_curriculum(context, curriculum_id, curriculum_name)
            if not curriculum:
                return CommandResult(
                    success=False,
                    message="Curriculum not found"
                )
            
            # Show curriculum info
            context.formatter.warning("About to delete curriculum:")
            summary = {
                'ID': curriculum['id'],
                'Name': curriculum['name'],
                'Status': curriculum['status'],
                'Students': curriculum.get('students', 0),
                'Modules': len(curriculum.get('modules', []))
            }
            context.formatter.key_value_pairs(summary)
            
            # Check dependencies
            dependencies = await self._check_dependencies(context, curriculum['id'])
            if dependencies:
                context.formatter.warning("This curriculum has dependencies:")
                context.formatter.list_items(dependencies)
                
                if not parsed_args.cascade:
                    return CommandResult(
                        success=False,
                        message="Cannot delete curriculum with dependencies. Use --cascade to delete all related data."
                    )
            
            # Confirm deletion
            if not parsed_args.force:
                danger_message = f"This will permanently delete curriculum '{curriculum['name']}'"
                if dependencies:
                    danger_message += " and all its dependencies"
                
                if not self.confirm_action(danger_message + ". Are you sure?", default=False):
                    return CommandResult(
                        success=False,
                        message="Deletion cancelled"
                    )
            
            # Create backup if requested
            backup_path = None
            if not parsed_args.no_backup:
                backup_path = await self._create_backup(context, curriculum)
                context.formatter.info(f"Backup created: {backup_path}")
            
            # Perform deletion
            await self._delete_curriculum(context, curriculum['id'], parsed_args.cascade)
            
            context.formatter.success(
                f"Curriculum '{curriculum['name']}' deleted successfully"
            )
            
            return CommandResult(
                success=True,
                message="Curriculum deleted successfully",
                data={'deleted_curriculum_id': curriculum['id'], 'backup_path': backup_path}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to delete curriculum: {e}",
                error=e
            )
    
    async def _find_curriculum(self, context, curriculum_id: Optional[int], 
                              curriculum_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find curriculum by ID or name"""
        # Mock implementation
        curricula = [
            {
                'id': 1,
                'name': 'Python Fundamentals',
                'status': 'active',
                'students': 245,
                'modules': [{'id': 1}, {'id': 2}, {'id': 3}]
            }
        ]
        
        for curriculum in curricula:
            if curriculum_id and curriculum['id'] == curriculum_id:
                return curriculum
            elif curriculum_name and curriculum_name.lower() in curriculum['name'].lower():
                return curriculum
        
        return None
    
    async def _check_dependencies(self, context, curriculum_id: int) -> List[str]:
        """Check for curriculum dependencies"""
        # Mock implementation
        return [
            "245 enrolled students",
            "3 published modules",
            "18 completed assignments"
        ]
    
    async def _create_backup(self, context, curriculum: Dict[str, Any]) -> str:
        """Create backup of curriculum data"""
        # Mock implementation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"curriculum_{curriculum['id']}_{timestamp}.json"
        backup_path = Path("backups") / backup_filename
        
        # In real implementation, save curriculum data to backup file
        backup_path.parent.mkdir(exist_ok=True)
        with open(backup_path, 'w') as f:
            json.dump(curriculum, f, indent=2, default=str)
        
        return str(backup_path)
    
    async def _delete_curriculum(self, context, curriculum_id: int, cascade: bool):
        """Delete curriculum and optionally its dependencies"""
        # Mock implementation - replace with actual database deletion
        pass
