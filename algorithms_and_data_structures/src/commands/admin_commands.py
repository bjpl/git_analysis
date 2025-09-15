#!/usr/bin/env python3
"""
Admin Commands - Administrative operations and system management

This module provides:
- User management (create, update, delete, list users)
- System configuration management
- Database maintenance and backups
- Log management and monitoring
- Permission and role management
- System health checks and diagnostics
- Bulk operations and data migration
"""

import json
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

from .base import BaseCommand, CommandResult, CommandMetadata, CommandCategory
from ..ui.formatter import TerminalFormatter
from ..models.user import User
from ..core.exceptions import CLIError


class UserManagementCommand(BaseCommand):
    """Manage users in the system"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="user-manage",
            description="Manage users in the system",
            category=CommandCategory.ADMIN,
            aliases=["users", "user-admin"],
            examples=[
                "user-manage list",
                "user-manage create --email user@example.com --role student",
                "user-manage update 123 --role instructor",
                "user-manage delete 123",
                "user-manage bulk-import users.json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Manage system users"
        )
        
        # Subcommands
        subcommands = parser.add_subparsers(dest='action', help='User management actions')
        
        # List users
        list_parser = subcommands.add_parser('list', help='List users')
        list_parser.add_argument('--role', choices=['student', 'instructor', 'admin'], help='Filter by role')
        list_parser.add_argument('--status', choices=['active', 'inactive', 'suspended'], help='Filter by status')
        list_parser.add_argument('--format', choices=['table', 'json'], default='table')
        list_parser.add_argument('--limit', type=int, help='Limit number of results')
        list_parser.add_argument('--include-stats', action='store_true', help='Include user statistics')
        
        # Create user
        create_parser = subcommands.add_parser('create', help='Create new user')
        create_parser.add_argument('--email', required=True, help='User email')
        create_parser.add_argument('--name', help='Full name')
        create_parser.add_argument('--role', choices=['student', 'instructor', 'admin'], default='student')
        create_parser.add_argument('--password', help='Initial password (will be prompted if not provided)')
        create_parser.add_argument('--send-welcome', action='store_true', help='Send welcome email')
        
        # Update user
        update_parser = subcommands.add_parser('update', help='Update user')
        update_parser.add_argument('user_id', type=int, help='User ID to update')
        update_parser.add_argument('--email', help='New email')
        update_parser.add_argument('--name', help='New full name')
        update_parser.add_argument('--role', choices=['student', 'instructor', 'admin'], help='New role')
        update_parser.add_argument('--status', choices=['active', 'inactive', 'suspended'], help='New status')
        update_parser.add_argument('--reset-password', action='store_true', help='Reset password')
        
        # Delete user
        delete_parser = subcommands.add_parser('delete', help='Delete user')
        delete_parser.add_argument('user_id', type=int, help='User ID to delete')
        delete_parser.add_argument('--archive', action='store_true', help='Archive instead of delete')
        
        # Show user details
        show_parser = subcommands.add_parser('show', help='Show user details')
        show_parser.add_argument('user_id', type=int, help='User ID to show')
        show_parser.add_argument('--include-activity', action='store_true', help='Include recent activity')
        show_parser.add_argument('--include-progress', action='store_true', help='Include learning progress')
        
        # Bulk operations
        bulk_import_parser = subcommands.add_parser('bulk-import', help='Bulk import users')
        bulk_import_parser.add_argument('file', help='JSON/CSV file with user data')
        bulk_import_parser.add_argument('--format', choices=['json', 'csv'], help='File format (auto-detected if not specified)')
        bulk_import_parser.add_argument('--dry-run', action='store_true', help='Preview import without creating users')
        
        bulk_export_parser = subcommands.add_parser('bulk-export', help='Bulk export users')
        bulk_export_parser.add_argument('--format', choices=['json', 'csv'], default='json')
        bulk_export_parser.add_argument('--output', help='Output file path')
        bulk_export_parser.add_argument('--filter', help='Filter criteria (JSON)')
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            if not parsed_args.action:
                return CommandResult(
                    success=False,
                    message="Please specify an action: list, create, update, delete, show, bulk-import, or bulk-export"
                )
            
            # Check admin permissions
            if not await self._check_admin_permissions(context):
                return CommandResult(
                    success=False,
                    message="Admin permissions required for user management"
                )
            
            if parsed_args.action == 'list':
                return await self._list_users(context, parsed_args)
            elif parsed_args.action == 'create':
                return await self._create_user(context, parsed_args)
            elif parsed_args.action == 'update':
                return await self._update_user(context, parsed_args)
            elif parsed_args.action == 'delete':
                return await self._delete_user(context, parsed_args)
            elif parsed_args.action == 'show':
                return await self._show_user(context, parsed_args)
            elif parsed_args.action == 'bulk-import':
                return await self._bulk_import_users(context, parsed_args)
            elif parsed_args.action == 'bulk-export':
                return await self._bulk_export_users(context, parsed_args)
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"User management operation failed: {e}",
                error=e
            )
    
    async def _check_admin_permissions(self, context) -> bool:
        """Check if current user has admin permissions"""
        # Mock implementation - replace with actual permission check
        return True
    
    async def _list_users(self, context, args) -> CommandResult:
        """List users with filtering"""
        # Mock data - replace with actual database query
        users = [
            {
                'id': 1,
                'email': 'alice.johnson@example.com',
                'name': 'Alice Johnson',
                'role': 'student',
                'status': 'active',
                'created': '2024-01-10T09:00:00',
                'last_login': '2024-01-22T14:30:00',
                'curricula_enrolled': 3,
                'completion_rate': 78.5
            },
            {
                'id': 2,
                'email': 'bob.smith@example.com',
                'name': 'Bob Smith',
                'role': 'student',
                'status': 'active',
                'created': '2024-01-12T11:15:00',
                'last_login': '2024-01-21T16:45:00',
                'curricula_enrolled': 2,
                'completion_rate': 92.3
            },
            {
                'id': 3,
                'email': 'jane.doe@example.com',
                'name': 'Dr. Jane Doe',
                'role': 'instructor',
                'status': 'active',
                'created': '2024-01-05T08:30:00',
                'last_login': '2024-01-22T10:20:00',
                'courses_taught': 5,
                'students_taught': 245
            },
            {
                'id': 4,
                'email': 'admin@example.com',
                'name': 'System Admin',
                'role': 'admin',
                'status': 'active',
                'created': '2024-01-01T00:00:00',
                'last_login': '2024-01-22T09:00:00'
            }
        ]
        
        # Apply filters
        if args.role:
            users = [u for u in users if u['role'] == args.role]
        if args.status:
            users = [u for u in users if u['status'] == args.status]
        
        # Apply limit
        if args.limit:
            users = users[:args.limit]
        
        if not users:
            return CommandResult(
                success=True,
                message="No users found matching criteria"
            )
        
        # Display results
        if args.format == 'json':
            output = json.dumps(users, indent=2, default=str)
            print(output)
        else:
            context.formatter.header(f"Users ({len(users)})", level=2)
            
            if args.include_stats:
                headers = ['ID', 'Name', 'Email', 'Role', 'Status', 'Stats', 'Last Login']
            else:
                headers = ['ID', 'Name', 'Email', 'Role', 'Status', 'Last Login']
            
            table_data = []
            for user in users:
                row = {
                    'ID': user['id'],
                    'Name': user['name'],
                    'Email': user['email'],
                    'Role': user['role'].title(),
                    'Status': user['status'].upper(),
                    'Last Login': user.get('last_login', 'Never')[:10] if user.get('last_login') else 'Never'
                }
                
                if args.include_stats:
                    if user['role'] == 'student':
                        stats = f"{user.get('curricula_enrolled', 0)} enrolled, {user.get('completion_rate', 0):.0f}% complete"
                    elif user['role'] == 'instructor':
                        stats = f"{user.get('courses_taught', 0)} courses, {user.get('students_taught', 0)} students"
                    else:
                        stats = 'N/A'
                    row['Stats'] = stats
                
                table_data.append(row)
            
            context.formatter.table(table_data, headers)
        
        return CommandResult(
            success=True,
            message=f"Found {len(users)} user(s)",
            data={'users': users}
        )
    
    async def _create_user(self, context, args) -> CommandResult:
        """Create a new user"""
        # Validate email format
        if '@' not in args.email:
            return CommandResult(
                success=False,
                message="Invalid email format"
            )
        
        # Check if user already exists
        existing_user = await self._find_user_by_email(context, args.email)
        if existing_user:
            return CommandResult(
                success=False,
                message=f"User with email {args.email} already exists"
            )
        
        # Get password if not provided
        password = args.password
        if not password:
            import getpass
            password = getpass.getpass("Enter password for new user: ")
            if not password:
                return CommandResult(
                    success=False,
                    message="Password is required"
                )
        
        # Create user data
        user_data = {
            'email': args.email,
            'name': args.name or args.email.split('@')[0],
            'role': args.role,
            'password': password,  # Should be hashed in real implementation
            'status': 'active',
            'created': datetime.now().isoformat()
        }
        
        # Show preview
        if not args.force:
            context.formatter.header("User Creation Preview", level=2)
            preview_data = user_data.copy()
            preview_data['password'] = '***HIDDEN***'
            context.formatter.key_value_pairs(preview_data)
            
            if not self.confirm_action("Create this user?", default=True):
                return CommandResult(
                    success=False,
                    message="User creation cancelled"
                )
        
        # Create user
        user_id = await self._create_user_in_db(context, user_data)
        
        # Send welcome email if requested
        if args.send_welcome:
            await self._send_welcome_email(context, user_id, args.email)
            context.formatter.info("Welcome email sent")
        
        context.formatter.success(f"User created successfully (ID: {user_id})")
        
        return CommandResult(
            success=True,
            message=f"User created with ID {user_id}",
            data={'user_id': user_id, 'email': args.email}
        )
    
    async def _update_user(self, context, args) -> CommandResult:
        """Update an existing user"""
        # Find user
        user = await self._find_user_by_id(context, args.user_id)
        if not user:
            return CommandResult(
                success=False,
                message=f"User with ID {args.user_id} not found"
            )
        
        # Prepare updates
        updates = {}
        if args.email:
            # Check if new email is already taken
            existing = await self._find_user_by_email(context, args.email)
            if existing and existing['id'] != args.user_id:
                return CommandResult(
                    success=False,
                    message=f"Email {args.email} is already taken"
                )
            updates['email'] = args.email
        
        if args.name:
            updates['name'] = args.name
        if args.role:
            updates['role'] = args.role
        if args.status:
            updates['status'] = args.status
        if args.reset_password:
            import secrets
            import string
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            updates['password'] = new_password
            context.formatter.info(f"New password: {new_password}")
        
        if not updates:
            return CommandResult(
                success=False,
                message="No updates specified"
            )
        
        updates['updated'] = datetime.now().isoformat()
        
        # Show preview
        if not args.force:
            context.formatter.header(f"User Update Preview (ID: {args.user_id})", level=2)
            current_info = {
                'Current Email': user['email'],
                'Current Name': user['name'],
                'Current Role': user['role'],
                'Current Status': user['status']
            }
            context.formatter.key_value_pairs(current_info)
            
            context.formatter.header("Changes", level=3)
            preview_updates = updates.copy()
            if 'password' in preview_updates:
                preview_updates['password'] = '***RESET***'
            context.formatter.key_value_pairs(preview_updates)
            
            if not self.confirm_action("Apply these updates?", default=True):
                return CommandResult(
                    success=False,
                    message="Update cancelled"
                )
        
        # Apply updates
        await self._update_user_in_db(context, args.user_id, updates)
        
        context.formatter.success(f"User {user['name']} updated successfully")
        
        return CommandResult(
            success=True,
            message="User updated successfully",
            data={'user_id': args.user_id, 'updates': updates}
        )
    
    async def _delete_user(self, context, args) -> CommandResult:
        """Delete a user"""
        # Find user
        user = await self._find_user_by_id(context, args.user_id)
        if not user:
            return CommandResult(
                success=False,
                message=f"User with ID {args.user_id} not found"
            )
        
        # Check if user has dependencies
        dependencies = await self._check_user_dependencies(context, args.user_id)
        
        # Show user info and dependencies
        context.formatter.warning("About to delete user:")
        user_info = {
            'ID': user['id'],
            'Name': user['name'],
            'Email': user['email'],
            'Role': user['role'],
            'Status': user['status']
        }
        context.formatter.key_value_pairs(user_info)
        
        if dependencies:
            context.formatter.warning("This user has the following dependencies:")
            context.formatter.list_items(dependencies)
        
        # Confirm deletion
        if not args.force:
            action = "archive" if args.archive else "permanently delete"
            if not self.confirm_action(
                f"This will {action} user '{user['name']}'. Are you sure?", 
                default=False
            ):
                return CommandResult(
                    success=False,
                    message="Deletion cancelled"
                )
        
        # Perform deletion or archival
        if args.archive:
            await self._archive_user(context, args.user_id)
            action_performed = "archived"
        else:
            await self._delete_user_from_db(context, args.user_id)
            action_performed = "deleted"
        
        context.formatter.success(f"User '{user['name']}' {action_performed} successfully")
        
        return CommandResult(
            success=True,
            message=f"User {action_performed} successfully",
            data={'user_id': args.user_id, 'action': action_performed}
        )
    
    async def _show_user(self, context, args) -> CommandResult:
        """Show detailed user information"""
        # Find user
        user = await self._find_user_by_id(context, args.user_id)
        if not user:
            return CommandResult(
                success=False,
                message=f"User with ID {args.user_id} not found"
            )
        
        # Get additional data if requested
        if args.include_activity:
            user['recent_activity'] = await self._get_user_activity(context, args.user_id)
        
        if args.include_progress:
            user['progress'] = await self._get_user_progress(context, args.user_id)
        
        # Display user information
        context.formatter.header(f"User Details: {user['name']}", level=1)
        
        # Basic information
        basic_info = {
            'ID': user['id'],
            'Email': user['email'],
            'Name': user['name'],
            'Role': user['role'].title(),
            'Status': user['status'].upper(),
            'Created': user['created'][:16],
            'Last Login': user.get('last_login', 'Never')[:16] if user.get('last_login') else 'Never'
        }
        context.formatter.key_value_pairs(basic_info)
        
        # Role-specific information
        if user['role'] == 'student' and (user.get('curricula_enrolled') or user.get('completion_rate')):
            context.formatter.header("Student Information", level=2)
            student_info = {
                'Curricula Enrolled': user.get('curricula_enrolled', 0),
                'Overall Completion Rate': f"{user.get('completion_rate', 0):.1f}%"
            }
            context.formatter.key_value_pairs(student_info)
        
        elif user['role'] == 'instructor' and (user.get('courses_taught') or user.get('students_taught')):
            context.formatter.header("Instructor Information", level=2)
            instructor_info = {
                'Courses Taught': user.get('courses_taught', 0),
                'Students Taught': user.get('students_taught', 0)
            }
            context.formatter.key_value_pairs(instructor_info)
        
        # Recent activity
        if args.include_activity and user.get('recent_activity'):
            context.formatter.header("Recent Activity", level=2)
            for activity in user['recent_activity']:
                context.formatter.info(f"  {activity['timestamp'][:16]} - {activity['description']}")
        
        # Progress information
        if args.include_progress and user.get('progress'):
            context.formatter.header("Learning Progress", level=2)
            progress_data = []
            for curriculum in user['progress']:
                progress_data.append({
                    'Curriculum': curriculum['name'],
                    'Progress': f"{curriculum['completion']:.1f}%",
                    'Score': f"{curriculum['avg_score']:.1f}%" if curriculum.get('avg_score') else 'N/A'
                })
            context.formatter.table(progress_data)
        
        return CommandResult(
            success=True,
            data={'user': user}
        )
    
    async def _bulk_import_users(self, context, args) -> CommandResult:
        """Bulk import users from file"""
        file_path = Path(args.file)
        if not file_path.exists():
            return CommandResult(
                success=False,
                message=f"File not found: {args.file}"
            )
        
        # Detect format if not specified
        file_format = args.format or ('json' if file_path.suffix == '.json' else 'csv')
        
        # Load user data
        if file_format == 'json':
            with open(file_path, 'r') as f:
                users_data = json.load(f)
        else:  # CSV
            import csv
            users_data = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                users_data = list(reader)
        
        # Validate user data
        validation_errors = []
        for i, user_data in enumerate(users_data):
            errors = self._validate_user_data(user_data)
            if errors:
                validation_errors.extend([f"Row {i+1}: {error}" for error in errors])
        
        if validation_errors:
            return CommandResult(
                success=False,
                message="Validation errors:\n" + "\n".join(validation_errors[:10]) + 
                       (f"\n... and {len(validation_errors) - 10} more errors" if len(validation_errors) > 10 else "")
            )
        
        # Show preview
        context.formatter.header(f"Bulk Import Preview ({len(users_data)} users)", level=2)
        
        # Show first few users
        preview_data = []
        for user in users_data[:5]:
            preview_data.append({
                'Email': user['email'],
                'Name': user.get('name', 'N/A'),
                'Role': user.get('role', 'student')
            })
        context.formatter.table(preview_data)
        
        if len(users_data) > 5:
            context.formatter.info(f"... and {len(users_data) - 5} more users")
        
        if args.dry_run:
            return CommandResult(
                success=True,
                message=f"Dry run completed. {len(users_data)} users would be imported",
                data={'users_count': len(users_data), 'validation_passed': True}
            )
        
        # Confirm import
        if not args.force:
            if not self.confirm_action(f"Import {len(users_data)} users?", default=True):
                return CommandResult(
                    success=False,
                    message="Import cancelled"
                )
        
        # Import users
        successful_imports = 0
        failed_imports = []
        
        with context.formatter.progress_bar(len(users_data), "Importing users") as pbar:
            for i, user_data in enumerate(users_data):
                try:
                    # Check if user already exists
                    existing = await self._find_user_by_email(context, user_data['email'])
                    if existing:
                        failed_imports.append((i + 1, f"User {user_data['email']} already exists"))
                        continue
                    
                    # Create user
                    user_data.setdefault('role', 'student')
                    user_data.setdefault('status', 'active')
                    user_data['created'] = datetime.now().isoformat()
                    
                    await self._create_user_in_db(context, user_data)
                    successful_imports += 1
                    
                except Exception as e:
                    failed_imports.append((i + 1, str(e)))
                
                pbar.update()
        
        # Show results
        if failed_imports:
            context.formatter.warning(f"{len(failed_imports)} imports failed:")
            for row_num, error in failed_imports[:5]:  # Show first 5 errors
                context.formatter.error(f"Row {row_num}: {error}")
            
            if len(failed_imports) > 5:
                context.formatter.info(f"... and {len(failed_imports) - 5} more errors")
        
        context.formatter.success(
            f"Bulk import completed: {successful_imports}/{len(users_data)} successful"
        )
        
        return CommandResult(
            success=len(failed_imports) == 0,
            message=f"Imported {successful_imports} users, {len(failed_imports)} failed",
            data={
                'successful_imports': successful_imports,
                'failed_imports': len(failed_imports),
                'errors': failed_imports
            }
        )
    
    async def _bulk_export_users(self, context, args) -> CommandResult:
        """Bulk export users to file"""
        # Get users (with optional filtering)
        filter_criteria = {}
        if args.filter:
            try:
                filter_criteria = json.loads(args.filter)
            except json.JSONDecodeError:
                return CommandResult(
                    success=False,
                    message="Invalid filter JSON format"
                )
        
        # Mock data - replace with actual database query with filters
        users = await self._get_users_for_export(context, filter_criteria)
        
        if not users:
            return CommandResult(
                success=True,
                message="No users found for export"
            )
        
        # Determine output file
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"users_export_{timestamp}.{args.format}"
        
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export users
        if args.format == 'json':
            with open(output_path, 'w') as f:
                json.dump(users, f, indent=2, default=str)
        else:  # CSV
            import csv
            with open(output_path, 'w', newline='') as f:
                if users:
                    writer = csv.DictWriter(f, fieldnames=users[0].keys())
                    writer.writeheader()
                    writer.writerows(users)
        
        context.formatter.success(f"Exported {len(users)} users to {output_path}")
        
        return CommandResult(
            success=True,
            message=f"Exported {len(users)} users",
            data={'export_path': str(output_path), 'user_count': len(users)}
        )
    
    # Helper methods
    async def _find_user_by_email(self, context, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        # Mock implementation - replace with actual database query
        return None  # User not found
    
    async def _find_user_by_id(self, context, user_id: int) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        # Mock implementation
        if user_id == 1:
            return {
                'id': 1,
                'email': 'alice.johnson@example.com',
                'name': 'Alice Johnson',
                'role': 'student',
                'status': 'active',
                'created': '2024-01-10T09:00:00',
                'last_login': '2024-01-22T14:30:00'
            }
        return None
    
    async def _create_user_in_db(self, context, user_data: Dict[str, Any]) -> int:
        """Create user in database"""
        # Mock implementation - replace with actual database creation
        user_id = hash(user_data['email'] + str(datetime.now())) % 10000
        return user_id
    
    async def _update_user_in_db(self, context, user_id: int, updates: Dict[str, Any]):
        """Update user in database"""
        # Mock implementation - replace with actual database update
        pass
    
    async def _delete_user_from_db(self, context, user_id: int):
        """Delete user from database"""
        # Mock implementation - replace with actual database deletion
        pass
    
    async def _archive_user(self, context, user_id: int):
        """Archive user instead of deleting"""
        # Mock implementation - replace with actual user archival
        pass
    
    async def _check_user_dependencies(self, context, user_id: int) -> List[str]:
        """Check for user dependencies"""
        # Mock implementation
        return [
            "3 curricula enrollments",
            "15 completed assignments",
            "2 forum posts"
        ]
    
    async def _send_welcome_email(self, context, user_id: int, email: str):
        """Send welcome email to new user"""
        # Mock implementation - replace with actual email sending
        pass
    
    async def _get_user_activity(self, context, user_id: int) -> List[Dict[str, Any]]:
        """Get recent user activity"""
        # Mock implementation
        return [
            {'timestamp': '2024-01-22T14:30:00', 'description': 'Completed Python Variables lesson'},
            {'timestamp': '2024-01-22T10:15:00', 'description': 'Started Python Fundamentals curriculum'},
            {'timestamp': '2024-01-21T16:45:00', 'description': 'Logged in'}
        ]
    
    async def _get_user_progress(self, context, user_id: int) -> List[Dict[str, Any]]:
        """Get user learning progress"""
        # Mock implementation
        return [
            {'name': 'Python Fundamentals', 'completion': 78.5, 'avg_score': 91.2},
            {'name': 'Web Development', 'completion': 34.2, 'avg_score': 87.8}
        ]
    
    async def _get_users_for_export(self, context, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get users for export with filtering"""
        # Mock implementation - would apply filters in actual database query
        return [
            {
                'id': 1,
                'email': 'alice.johnson@example.com',
                'name': 'Alice Johnson',
                'role': 'student',
                'status': 'active',
                'created': '2024-01-10T09:00:00'
            }
        ]
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> List[str]:
        """Validate user data for import"""
        errors = []
        
        if not user_data.get('email'):
            errors.append("Email is required")
        elif '@' not in user_data['email']:
            errors.append("Invalid email format")
        
        if 'role' in user_data and user_data['role'] not in ['student', 'instructor', 'admin']:
            errors.append("Invalid role")
        
        if 'status' in user_data and user_data['status'] not in ['active', 'inactive', 'suspended']:
            errors.append("Invalid status")
        
        return errors


class SystemConfigCommand(BaseCommand):
    """Manage system configuration"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="system-config",
            description="Manage system configuration settings",
            category=CommandCategory.ADMIN,
            aliases=["config", "settings"],
            examples=[
                "system-config list",
                "system-config get database.host",
                "system-config set email.smtp_server smtp.example.com",
                "system-config export config_backup.json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Manage system configuration"
        )
        
        # Subcommands
        subcommands = parser.add_subparsers(dest='action', help='Configuration actions')
        
        # List configuration
        list_parser = subcommands.add_parser('list', help='List configuration settings')
        list_parser.add_argument('--category', help='Filter by category')
        list_parser.add_argument('--format', choices=['table', 'json'], default='table')
        
        # Get configuration value
        get_parser = subcommands.add_parser('get', help='Get configuration value')
        get_parser.add_argument('key', help='Configuration key (dot notation supported)')
        
        # Set configuration value
        set_parser = subcommands.add_parser('set', help='Set configuration value')
        set_parser.add_argument('key', help='Configuration key')
        set_parser.add_argument('value', help='Configuration value')
        set_parser.add_argument('--type', choices=['string', 'int', 'float', 'bool', 'json'], default='string')
        
        # Export configuration
        export_parser = subcommands.add_parser('export', help='Export configuration')
        export_parser.add_argument('output_file', help='Output file path')
        export_parser.add_argument('--format', choices=['json', 'yaml'], default='json')
        
        # Import configuration
        import_parser = subcommands.add_parser('import', help='Import configuration')
        import_parser.add_argument('input_file', help='Input file path')
        import_parser.add_argument('--merge', action='store_true', help='Merge with existing config')
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            if not parsed_args.action:
                return CommandResult(
                    success=False,
                    message="Please specify an action: list, get, set, export, or import"
                )
            
            # Check admin permissions
            if not await self._check_admin_permissions(context):
                return CommandResult(
                    success=False,
                    message="Admin permissions required for system configuration"
                )
            
            if parsed_args.action == 'list':
                return await self._list_config(context, parsed_args)
            elif parsed_args.action == 'get':
                return await self._get_config(context, parsed_args)
            elif parsed_args.action == 'set':
                return await self._set_config(context, parsed_args)
            elif parsed_args.action == 'export':
                return await self._export_config(context, parsed_args)
            elif parsed_args.action == 'import':
                return await self._import_config(context, parsed_args)
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Configuration operation failed: {e}",
                error=e
            )
    
    async def _check_admin_permissions(self, context) -> bool:
        """Check admin permissions"""
        # Mock implementation
        return True
    
    async def _list_config(self, context, args) -> CommandResult:
        """List configuration settings"""
        # Mock configuration data
        config = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'curriculum_db',
                'ssl_enabled': True
            },
            'email': {
                'smtp_server': 'smtp.example.com',
                'smtp_port': 587,
                'use_tls': True,
                'from_address': 'noreply@example.com'
            },
            'system': {
                'max_file_size_mb': 50,
                'session_timeout_minutes': 30,
                'debug_mode': False
            },
            'features': {
                'user_registration_enabled': True,
                'email_verification_required': True,
                'search_analytics_enabled': True
            }
        }
        
        # Filter by category if specified
        if args.category:
            if args.category in config:
                config = {args.category: config[args.category]}
            else:
                return CommandResult(
                    success=False,
                    message=f"Category '{args.category}' not found"
                )
        
        # Display configuration
        if args.format == 'json':
            output = json.dumps(config, indent=2)
            print(output)
        else:
            context.formatter.header("System Configuration", level=2)
            
            for category, settings in config.items():
                context.formatter.header(category.title(), level=3)
                config_data = []
                for key, value in settings.items():
                    config_data.append({
                        'Setting': key,
                        'Value': str(value),
                        'Type': type(value).__name__
                    })
                context.formatter.table(config_data)
                print()
        
        return CommandResult(
            success=True,
            data={'config': config}
        )
    
    async def _get_config(self, context, args) -> CommandResult:
        """Get specific configuration value"""
        # Mock implementation - would get from actual config store
        config_value = await self._get_config_value(context, args.key)
        
        if config_value is None:
            return CommandResult(
                success=False,
                message=f"Configuration key '{args.key}' not found"
            )
        
        context.formatter.info(f"{args.key}: {config_value}")
        
        return CommandResult(
            success=True,
            data={'key': args.key, 'value': config_value}
        )
    
    async def _set_config(self, context, args) -> CommandResult:
        """Set configuration value"""
        # Parse value according to type
        try:
            if args.type == 'int':
                parsed_value = int(args.value)
            elif args.type == 'float':
                parsed_value = float(args.value)
            elif args.type == 'bool':
                parsed_value = args.value.lower() in ['true', '1', 'yes', 'on']
            elif args.type == 'json':
                parsed_value = json.loads(args.value)
            else:  # string
                parsed_value = args.value
        except (ValueError, json.JSONDecodeError) as e:
            return CommandResult(
                success=False,
                message=f"Invalid value for type {args.type}: {e}"
            )
        
        # Get current value for comparison
        current_value = await self._get_config_value(context, args.key)
        
        # Show change preview
        if not args.force:
            context.formatter.header("Configuration Change Preview", level=2)
            change_info = {
                'Key': args.key,
                'Current Value': str(current_value) if current_value is not None else 'Not set',
                'New Value': str(parsed_value),
                'Type': args.type
            }
            context.formatter.key_value_pairs(change_info)
            
            if not self.confirm_action("Apply this configuration change?", default=True):
                return CommandResult(
                    success=False,
                    message="Configuration change cancelled"
                )
        
        # Set the configuration value
        await self._set_config_value(context, args.key, parsed_value)
        
        context.formatter.success(f"Configuration '{args.key}' updated successfully")
        
        return CommandResult(
            success=True,
            message="Configuration updated",
            data={'key': args.key, 'old_value': current_value, 'new_value': parsed_value}
        )
    
    async def _export_config(self, context, args) -> CommandResult:
        """Export configuration to file"""
        # Get all configuration
        config = await self._get_all_config(context)
        
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export based on format
        if args.format == 'json':
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2, default=str)
        else:  # YAML
            try:
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            except ImportError:
                return CommandResult(
                    success=False,
                    message="PyYAML package required for YAML export"
                )
        
        context.formatter.success(f"Configuration exported to {output_path}")
        
        return CommandResult(
            success=True,
            message="Configuration exported",
            data={'export_path': str(output_path)}
        )
    
    async def _import_config(self, context, args) -> CommandResult:
        """Import configuration from file"""
        input_path = Path(args.input_file)
        if not input_path.exists():
            return CommandResult(
                success=False,
                message=f"File not found: {args.input_file}"
            )
        
        # Load configuration
        try:
            if input_path.suffix == '.json':
                with open(input_path, 'r') as f:
                    import_config = json.load(f)
            else:  # Assume YAML
                import yaml
                with open(input_path, 'r') as f:
                    import_config = yaml.safe_load(f)
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to load configuration file: {e}"
            )
        
        # Show preview
        context.formatter.header("Configuration Import Preview", level=2)
        
        config_count = self._count_config_items(import_config)
        context.formatter.info(f"Configuration items to import: {config_count}")
        
        if args.merge:
            context.formatter.warning("This will merge with existing configuration")
        else:
            context.formatter.warning("This will replace existing configuration")
        
        # Show sample of configuration
        sample_config = dict(list(import_config.items())[:3])  # First 3 categories
        context.formatter.header("Sample Configuration", level=3)
        for category, settings in sample_config.items():
            context.formatter.info(f"{category}: {len(settings)} settings")
        
        if not args.force:
            if not self.confirm_action("Import this configuration?", default=False):
                return CommandResult(
                    success=False,
                    message="Configuration import cancelled"
                )
        
        # Import configuration
        await self._import_config_data(context, import_config, args.merge)
        
        context.formatter.success("Configuration imported successfully")
        
        return CommandResult(
            success=True,
            message="Configuration imported",
            data={'items_imported': config_count, 'merge_mode': args.merge}
        )
    
    # Helper methods
    async def _get_config_value(self, context, key: str) -> Any:
        """Get configuration value by key"""
        # Mock implementation
        config = {
            'database.host': 'localhost',
            'database.port': 5432,
            'email.smtp_server': 'smtp.example.com',
            'system.debug_mode': False
        }
        return config.get(key)
    
    async def _set_config_value(self, context, key: str, value: Any):
        """Set configuration value"""
        # Mock implementation - would save to actual config store
        pass
    
    async def _get_all_config(self, context) -> Dict[str, Any]:
        """Get all configuration"""
        # Mock implementation
        return {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'curriculum_db'
            },
            'email': {
                'smtp_server': 'smtp.example.com',
                'smtp_port': 587
            }
        }
    
    async def _import_config_data(self, context, config_data: Dict[str, Any], merge: bool):
        """Import configuration data"""
        # Mock implementation - would save to actual config store
        pass
    
    def _count_config_items(self, config: Dict[str, Any]) -> int:
        """Count total configuration items"""
        total = 0
        for value in config.values():
            if isinstance(value, dict):
                total += len(value)
            else:
                total += 1
        return total


class SystemHealthCommand(BaseCommand):
    """Check system health and status"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="system-health",
            description="Check system health and status",
            category=CommandCategory.ADMIN,
            aliases=["health", "status"],
            examples=[
                "system-health",
                "system-health --detailed",
                "system-health --component database",
                "system-health --export health_report.json"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Check system health and status"
        )
        
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed health information'
        )
        parser.add_argument(
            '--component',
            choices=['database', 'cache', 'storage', 'email', 'search'],
            help='Check specific component only'
        )
        parser.add_argument(
            '--format',
            choices=['report', 'json'],
            default='report',
            help='Output format'
        )
        parser.add_argument(
            '--export',
            help='Export health report to file'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Check admin permissions
            if not await self._check_admin_permissions(context):
                return CommandResult(
                    success=False,
                    message="Admin permissions required for system health checks"
                )
            
            # Generate health report
            health_data = await self._generate_health_report(context, parsed_args)
            
            # Display report
            if parsed_args.format == 'json':
                output = json.dumps(health_data, indent=2, default=str)
                print(output)
            else:
                self._show_health_report(context.formatter, health_data, parsed_args)
            
            # Export if requested
            if parsed_args.export:
                export_path = await self._export_health_report(context, health_data, parsed_args.export)
                context.formatter.success(f"Health report exported to: {export_path}")
            
            # Determine overall success based on component health
            overall_healthy = all(
                component['status'] in ['healthy', 'warning'] 
                for component in health_data['components'].values()
            )
            
            return CommandResult(
                success=True,
                message=f"System health check completed - {'Healthy' if overall_healthy else 'Issues detected'}",
                data={'health': health_data, 'overall_healthy': overall_healthy}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Health check failed: {e}",
                error=e
            )
    
    async def _check_admin_permissions(self, context) -> bool:
        """Check admin permissions"""
        return True
    
    async def _generate_health_report(self, context, args) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': await self._get_system_info(context),
            'components': {},
            'overall_status': 'healthy'
        }
        
        # Check specific component or all components
        if args.component:
            components_to_check = [args.component]
        else:
            components_to_check = ['database', 'cache', 'storage', 'email', 'search']
        
        # Check each component
        for component in components_to_check:
            health_report['components'][component] = await self._check_component_health(
                context, component, args.detailed
            )
        
        # Determine overall status
        statuses = [comp['status'] for comp in health_report['components'].values()]
        if 'critical' in statuses:
            health_report['overall_status'] = 'critical'
        elif 'error' in statuses:
            health_report['overall_status'] = 'error'
        elif 'warning' in statuses:
            health_report['overall_status'] = 'warning'
        else:
            health_report['overall_status'] = 'healthy'
        
        return health_report
    
    async def _get_system_info(self, context) -> Dict[str, Any]:
        """Get general system information"""
        import psutil
        import platform
        
        return {
            'platform': platform.system(),
            'platform_version': platform.release(),
            'python_version': platform.python_version(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'uptime_seconds': int(psutil.boot_time()),
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    async def _check_component_health(self, context, component: str, detailed: bool) -> Dict[str, Any]:
        """Check health of specific component"""
        # Mock implementation - replace with actual health checks
        if component == 'database':
            return {
                'status': 'healthy',
                'response_time_ms': 25.3,
                'connections_active': 12,
                'connections_max': 100,
                'last_backup': '2024-01-22T02:00:00',
                'disk_usage_percent': 67.3,
                'details': {
                    'host': 'localhost:5432',
                    'database': 'curriculum_db',
                    'version': 'PostgreSQL 14.2',
                    'table_count': 23,
                    'total_size_mb': 245.7
                } if detailed else None
            }
        elif component == 'cache':
            return {
                'status': 'healthy',
                'response_time_ms': 1.8,
                'memory_usage_mb': 128.5,
                'memory_max_mb': 512,
                'hit_rate_percent': 89.3,
                'keys_count': 1847,
                'details': {
                    'host': 'localhost:6379',
                    'version': 'Redis 6.2.7',
                    'evicted_keys': 23,
                    'expired_keys': 156
                } if detailed else None
            }
        elif component == 'storage':
            return {
                'status': 'warning',
                'disk_usage_percent': 85.2,
                'available_space_gb': 12.4,
                'total_files': 8947,
                'backup_status': 'healthy',
                'details': {
                    'mount_point': '/var/data',
                    'filesystem': 'ext4',
                    'last_cleanup': '2024-01-20T03:00:00',
                    'largest_files': [
                        {'name': 'video_archive.zip', 'size_mb': 1024.5},
                        {'name': 'database_backup.sql', 'size_mb': 567.2}
                    ]
                } if detailed else None
            }
        elif component == 'email':
            return {
                'status': 'healthy',
                'smtp_connection': 'connected',
                'queue_size': 3,
                'emails_sent_today': 47,
                'delivery_rate_percent': 98.5,
                'details': {
                    'smtp_server': 'smtp.example.com:587',
                    'auth_status': 'authenticated',
                    'last_sent': '2024-01-22T15:42:00',
                    'bounce_rate_percent': 1.2
                } if detailed else None
            }
        elif component == 'search':
            return {
                'status': 'healthy',
                'response_time_ms': 45.7,
                'index_size_mb': 89.3,
                'documents_indexed': 3421,
                'last_index_update': '2024-01-22T14:15:00',
                'details': {
                    'search_engine': 'Elasticsearch 7.15.2',
                    'cluster_health': 'green',
                    'active_shards': 5,
                    'queries_per_second': 12.4
                } if detailed else None
            }
        
        return {'status': 'unknown'}
    
    def _show_health_report(self, formatter: TerminalFormatter, health_data: Dict[str, Any], args):
        """Display health report"""
        # Overall status
        status_icon = {
            'healthy': '✅',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🔴'
        }.get(health_data['overall_status'], '❓')
        
        formatter.header(f"System Health Check {status_icon}", level=1)
        formatter.info(f"Status: {health_data['overall_status'].upper()}")
        formatter.info(f"Checked: {health_data['timestamp'][:16]}")
        
        # System information
        if args.detailed:
            formatter.header("System Information", level=2)
            sys_info = health_data['system_info']
            formatter.key_value_pairs({
                'Platform': f"{sys_info['platform']} {sys_info['platform_version']}",
                'Python Version': sys_info['python_version'],
                'CPU Usage': f"{sys_info['cpu_usage']:.1f}%",
                'Memory Usage': f"{sys_info['memory_usage']:.1f}%",
                'Disk Usage': f"{sys_info['disk_usage']:.1f}%"
            })
        
        # Component health
        formatter.header("Component Health", level=2)
        
        for component_name, component_health in health_data['components'].items():
            status_icon = {
                'healthy': '✅',
                'warning': '⚠️',
                'error': '❌',
                'critical': '🔴'
            }.get(component_health['status'], '❓')
            
            formatter.header(f"{component_name.title()} {status_icon}", level=3)
            
            # Basic metrics
            metrics = {}
            if 'response_time_ms' in component_health:
                metrics['Response Time'] = f"{component_health['response_time_ms']:.1f}ms"
            
            if component_name == 'database':
                metrics.update({
                    'Active Connections': f"{component_health['connections_active']}/{component_health['connections_max']}",
                    'Disk Usage': f"{component_health['disk_usage_percent']:.1f}%",
                    'Last Backup': component_health['last_backup'][:16]
                })
            elif component_name == 'cache':
                metrics.update({
                    'Memory Usage': f"{component_health['memory_usage_mb']:.1f}/{component_health['memory_max_mb']}MB",
                    'Hit Rate': f"{component_health['hit_rate_percent']:.1f}%",
                    'Keys': component_health['keys_count']
                })
            elif component_name == 'storage':
                metrics.update({
                    'Disk Usage': f"{component_health['disk_usage_percent']:.1f}%",
                    'Available Space': f"{component_health['available_space_gb']:.1f}GB",
                    'Total Files': component_health['total_files']
                })
            elif component_name == 'email':
                metrics.update({
                    'Queue Size': component_health['queue_size'],
                    'Emails Sent Today': component_health['emails_sent_today'],
                    'Delivery Rate': f"{component_health['delivery_rate_percent']:.1f}%"
                })
            elif component_name == 'search':
                metrics.update({
                    'Index Size': f"{component_health['index_size_mb']:.1f}MB",
                    'Documents': component_health['documents_indexed'],
                    'Last Update': component_health['last_index_update'][:16]
                })
            
            formatter.key_value_pairs(metrics, indent=1)
            
            # Detailed information
            if args.detailed and component_health.get('details'):
                formatter.info("  Details:")
                formatter.key_value_pairs(component_health['details'], indent=2)
            
            print()
    
    async def _export_health_report(self, context, health_data: Dict[str, Any], output_file: str) -> str:
        """Export health report to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(health_data, f, indent=2, default=str)
        
        return str(output_path)
