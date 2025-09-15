#!/usr/bin/env python3
"""
Search Commands - Search and discovery functionality

This module provides:
- Global search across curricula, content, and users
- Advanced search with filters and facets
- Search suggestions and autocomplete
- Search analytics and popular searches
- Saved searches and search history
- Full-text search with ranking
"""

import json
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from .base import BaseCommand, CommandResult, CommandMetadata, CommandCategory
from ..ui.formatter import TerminalFormatter
from ..core.exceptions import CLIError


class SearchCommand(BaseCommand):
    """Global search across all content types"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="search",
            description="Search across curricula, content, and users",
            category=CommandCategory.SYSTEM,
            aliases=["find", "query"],
            examples=[
                "search 'python basics'",
                "search --type curriculum 'web development'",
                "search --author 'jane smith' --difficulty beginner",
                "search 'machine learning' --tag ai --format json",
                "search --content-type lesson --status published 'introduction'"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Search across all content types"
        )
        
        # Search query
        parser.add_argument(
            'query',
            nargs='?',
            help='Search query string'
        )
        
        # Search scope
        parser.add_argument(
            '--type',
            choices=['all', 'curriculum', 'content', 'user', 'progress'],
            default='all',
            help='Limit search to specific type'
        )
        parser.add_argument(
            '--content-type',
            choices=['lesson', 'exercise', 'assessment', 'resource', 'video', 'quiz'],
            help='Filter by content type (when searching content)'
        )
        
        # Search filters
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
        parser.add_argument(
            '--status',
            help='Filter by status'
        )
        parser.add_argument(
            '--created-after',
            help='Filter by creation date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--created-before',
            help='Filter by creation date (YYYY-MM-DD)'
        )
        
        # Search options
        parser.add_argument(
            '--exact',
            action='store_true',
            help='Exact phrase search'
        )
        parser.add_argument(
            '--fuzzy',
            action='store_true',
            help='Enable fuzzy matching'
        )
        parser.add_argument(
            '--case-sensitive',
            action='store_true',
            help='Case-sensitive search'
        )
        
        # Output options
        parser.add_argument(
            '--format',
            choices=['list', 'detailed', 'json', 'summary'],
            default='list',
            help='Output format'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of results'
        )
        parser.add_argument(
            '--sort',
            choices=['relevance', 'date', 'title', 'score'],
            default='relevance',
            help='Sort results by'
        )
        parser.add_argument(
            '--include-preview',
            action='store_true',
            help='Include content preview in results'
        )
        
        # Search management
        parser.add_argument(
            '--save',
            help='Save search with given name'
        )
        parser.add_argument(
            '--suggest',
            action='store_true',
            help='Show search suggestions only'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Handle search suggestions
            if parsed_args.suggest:
                suggestions = await self._get_search_suggestions(context, parsed_args.query)
                self._show_suggestions(context.formatter, suggestions)
                return CommandResult(
                    success=True,
                    message=f"Found {len(suggestions)} suggestions",
                    data={'suggestions': suggestions}
                )
            
            # Require query for actual search
            if not parsed_args.query:
                return CommandResult(
                    success=False,
                    message="Search query is required (use --suggest for suggestions)"
                )
            
            # Perform search
            search_results = await self._perform_search(context, parsed_args)
            
            # Record search for analytics
            await self._record_search(context, parsed_args.query, len(search_results))
            
            # Save search if requested
            if parsed_args.save:
                await self._save_search(context, parsed_args.save, parsed_args)
                context.formatter.info(f"Search saved as '{parsed_args.save}'")
            
            # Display results
            if not search_results:
                context.formatter.warning("No results found")
                suggestions = await self._get_search_suggestions(context, parsed_args.query)
                if suggestions:
                    context.formatter.info("Did you mean:")
                    self._show_suggestions(context.formatter, suggestions[:3])
                
                return CommandResult(
                    success=True,
                    message="No results found"
                )
            
            # Format and display results
            if parsed_args.format == 'json':
                output = json.dumps(search_results, indent=2, default=str)
                print(output)
            elif parsed_args.format == 'summary':
                self._show_search_summary(context.formatter, search_results, parsed_args)
            elif parsed_args.format == 'detailed':
                self._show_detailed_results(context.formatter, search_results, parsed_args)
            else:
                self._show_list_results(context.formatter, search_results, parsed_args)
            
            return CommandResult(
                success=True,
                message=f"Found {len(search_results)} result(s)",
                data={'results': search_results, 'query': parsed_args.query}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Search failed: {e}",
                error=e
            )
    
    async def _perform_search(self, context, args) -> List[Dict[str, Any]]:
        """Perform the actual search operation"""
        # Mock search implementation - replace with actual search engine
        all_items = await self._get_searchable_items(context)
        
        # Apply type filter
        if args.type != 'all':
            all_items = [item for item in all_items if item['type'] == args.type]
        
        # Apply content type filter
        if args.content_type:
            all_items = [item for item in all_items if item.get('content_type') == args.content_type]
        
        # Apply other filters
        if args.author:
            all_items = [item for item in all_items if args.author.lower() in item.get('author', '').lower()]
        
        if args.difficulty:
            all_items = [item for item in all_items if item.get('difficulty') == args.difficulty]
        
        if args.status:
            all_items = [item for item in all_items if item.get('status') == args.status]
        
        if args.tag:
            for tag in args.tag:
                all_items = [item for item in all_items if tag.lower() in [t.lower() for t in item.get('tags', [])]]
        
        # Date filters
        if args.created_after or args.created_before:
            after_date = datetime.fromisoformat(args.created_after) if args.created_after else None
            before_date = datetime.fromisoformat(args.created_before) if args.created_before else None
            
            filtered_items = []
            for item in all_items:
                created_date = datetime.fromisoformat(item['created']) if item.get('created') else None
                if created_date:
                    if after_date and created_date < after_date:
                        continue
                    if before_date and created_date > before_date:
                        continue
                filtered_items.append(item)
            all_items = filtered_items
        
        # Apply text search
        query = args.query.lower()
        search_results = []
        
        for item in all_items:
            score = self._calculate_relevance_score(item, query, args)
            if score > 0:
                result_item = item.copy()
                result_item['relevance_score'] = score
                result_item['search_snippet'] = self._generate_snippet(item, query)
                search_results.append(result_item)
        
        # Sort results
        if args.sort == 'relevance':
            search_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        elif args.sort == 'date':
            search_results.sort(key=lambda x: x.get('created', ''), reverse=True)
        elif args.sort == 'title':
            search_results.sort(key=lambda x: x.get('title', ''))
        elif args.sort == 'score':
            search_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Apply limit
        return search_results[:args.limit]
    
    async def _get_searchable_items(self, context) -> List[Dict[str, Any]]:
        """Get all searchable items from the system"""
        # Mock data - replace with actual database queries
        return [
            {
                'id': 1,
                'type': 'curriculum',
                'title': 'Python Fundamentals',
                'description': 'Learn Python programming from basics to advanced concepts',
                'author': 'Jane Smith',
                'difficulty': 'beginner',
                'status': 'published',
                'tags': ['python', 'programming', 'fundamentals'],
                'created': '2024-01-15T10:30:00',
                'score': 4.8,
                'popularity': 245
            },
            {
                'id': 2,
                'type': 'content',
                'content_type': 'lesson',
                'title': 'Introduction to Python',
                'description': 'Learn the basics of Python programming language',
                'body': 'Python is a high-level programming language that is widely used for web development, data science, and automation.',
                'author': 'Jane Smith',
                'difficulty': 'beginner',
                'status': 'published',
                'tags': ['python', 'basics', 'introduction'],
                'created': '2024-01-15T11:00:00',
                'score': 4.7,
                'views': 1250
            },
            {
                'id': 3,
                'type': 'content',
                'content_type': 'exercise',
                'title': 'Python Variables Practice',
                'description': 'Practice working with variables in Python',
                'body': 'Complete the following exercises to practice creating and using variables in Python.',
                'author': 'John Doe',
                'difficulty': 'beginner',
                'status': 'published',
                'tags': ['python', 'variables', 'practice'],
                'created': '2024-01-16T09:30:00',
                'score': 4.5,
                'completion_rate': 87.3
            },
            {
                'id': 4,
                'type': 'curriculum',
                'title': 'Web Development with JavaScript',
                'description': 'Master modern web development using JavaScript, HTML, and CSS',
                'author': 'Alice Johnson',
                'difficulty': 'intermediate',
                'status': 'published',
                'tags': ['javascript', 'web', 'html', 'css'],
                'created': '2024-01-10T14:20:00',
                'score': 4.6,
                'popularity': 189
            },
            {
                'id': 5,
                'type': 'user',
                'title': 'Dr. Jane Smith',
                'description': 'Senior Python Developer and Educator',
                'role': 'instructor',
                'specialties': ['python', 'data science', 'machine learning'],
                'created': '2024-01-01T00:00:00',
                'courses_taught': 12,
                'rating': 4.9
            }
        ]
    
    def _calculate_relevance_score(self, item: Dict[str, Any], query: str, args) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        query_words = query.split() if not args.exact else [query]
        
        # Title matching (highest weight)
        title = item.get('title', '').lower()
        for word in query_words:
            if args.exact:
                if word in title:
                    score += 10.0
            else:
                if word in title:
                    score += 5.0
                elif args.fuzzy and self._fuzzy_match(word, title):
                    score += 3.0
        
        # Description matching (medium weight)
        description = item.get('description', '').lower()
        for word in query_words:
            if args.exact:
                if word in description:
                    score += 5.0
            else:
                if word in description:
                    score += 2.0
                elif args.fuzzy and self._fuzzy_match(word, description):
                    score += 1.0
        
        # Body content matching (lower weight)
        body = item.get('body', '').lower()
        for word in query_words:
            if word in body:
                score += 1.0
        
        # Tag matching (medium-high weight)
        tags = [tag.lower() for tag in item.get('tags', [])]
        for word in query_words:
            if word in tags:
                score += 4.0
        
        # Author matching
        author = item.get('author', '').lower()
        if query in author:
            score += 3.0
        
        # Boost popular/high-quality content
        if item.get('score'):
            score *= (1 + item['score'] / 10.0)
        
        if item.get('popularity'):
            score *= (1 + min(item['popularity'] / 1000.0, 0.5))
        
        if item.get('views'):
            score *= (1 + min(item['views'] / 5000.0, 0.3))
        
        return score
    
    def _fuzzy_match(self, word: str, text: str) -> bool:
        """Simple fuzzy matching implementation"""
        # Simple Levenshtein-like fuzzy matching
        for text_word in text.split():
            if len(word) > 3 and len(text_word) > 3:
                # Allow 1-2 character differences
                max_diff = min(2, len(word) // 3)
                diff_count = 0
                min_len = min(len(word), len(text_word))
                
                for i in range(min_len):
                    if word[i] != text_word[i]:
                        diff_count += 1
                        if diff_count > max_diff:
                            break
                
                if diff_count <= max_diff:
                    return True
        return False
    
    def _generate_snippet(self, item: Dict[str, Any], query: str) -> str:
        """Generate search result snippet"""
        text_fields = ['description', 'body']
        snippet = ""
        
        for field in text_fields:
            text = item.get(field, '')
            if text and query.lower() in text.lower():
                # Find the query in the text and extract surrounding context
                index = text.lower().find(query.lower())
                start = max(0, index - 50)
                end = min(len(text), index + len(query) + 50)
                
                snippet = text[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                break
        
        return snippet[:150] if snippet else (item.get('description', '') or '')[:150]
    
    async def _get_search_suggestions(self, context, query: Optional[str]) -> List[str]:
        """Get search suggestions based on query"""
        # Mock suggestions - replace with actual suggestion engine
        popular_searches = [
            'python basics',
            'web development',
            'javascript fundamentals',
            'data science',
            'machine learning',
            'html css tutorial',
            'python advanced',
            'react framework',
            'database design',
            'api development'
        ]
        
        if not query:
            return popular_searches[:5]
        
        # Filter suggestions based on query
        query = query.lower()
        suggestions = [s for s in popular_searches if query in s.lower()]
        
        # Add some dynamic suggestions
        if 'python' in query:
            suggestions.extend(['python variables', 'python functions', 'python classes'])
        elif 'web' in query:
            suggestions.extend(['web design', 'web security', 'web APIs'])
        elif 'javascript' in query or 'js' in query:
            suggestions.extend(['javascript async', 'javascript dom', 'javascript es6'])
        
        return suggestions[:8]
    
    async def _record_search(self, context, query: str, result_count: int):
        """Record search for analytics"""
        # Mock implementation - replace with actual analytics recording
        search_record = {
            'query': query,
            'result_count': result_count,
            'timestamp': datetime.now().isoformat(),
            'user_id': getattr(context, 'user_id', None)
        }
        # In real implementation: await search_analytics.record(search_record)
    
    async def _save_search(self, context, search_name: str, args):
        """Save search for later use"""
        # Mock implementation - replace with actual search saving
        saved_search = {
            'name': search_name,
            'query': args.query,
            'filters': {
                'type': args.type,
                'content_type': args.content_type,
                'author': args.author,
                'difficulty': args.difficulty,
                'status': args.status,
                'tags': args.tag,
            },
            'options': {
                'exact': args.exact,
                'fuzzy': args.fuzzy,
                'case_sensitive': args.case_sensitive
            },
            'created': datetime.now().isoformat()
        }
        # In real implementation: await saved_searches.save(saved_search)
    
    def _show_suggestions(self, formatter: TerminalFormatter, suggestions: List[str]):
        """Show search suggestions"""
        formatter.header("Search Suggestions", level=2)
        for suggestion in suggestions:
            formatter.info(f"ὐd {suggestion}")
    
    def _show_list_results(self, formatter: TerminalFormatter, results: List[Dict[str, Any]], args):
        """Show search results in list format"""
        formatter.header(f"Search Results ({len(results)} found)", level=2)
        
        for i, result in enumerate(results, 1):
            # Result type icon
            type_icons = {
                'curriculum': '📚',
                'content': '📄',
                'user': '👤',
                'progress': '📈'
            }
            icon = type_icons.get(result['type'], '📄')
            
            # Content type for content items
            content_type = ""
            if result['type'] == 'content' and result.get('content_type'):
                content_icons = {
                    'lesson': '📺',
                    'exercise': '💪',
                    'quiz': '❓',
                    'assessment': '📊',
                    'resource': '📁',
                    'video': '🎥'
                }
                content_icon = content_icons.get(result['content_type'], '📄')
                content_type = f" {content_icon}"
            
            # Result header
            score_text = f" ({result['relevance_score']:.1f})" if args.sort == 'relevance' else ""
            formatter.info(f"{i:2d}. {icon}{content_type} {result['title']}{score_text}")
            
            # Metadata
            metadata = []
            if result.get('author'):
                metadata.append(f"by {result['author']}")
            if result.get('difficulty'):
                metadata.append(result['difficulty'])
            if result.get('status'):
                metadata.append(result['status'])
            
            if metadata:
                formatter.info(f"    {' | '.join(metadata)}")
            
            # Snippet or description
            snippet = result.get('search_snippet', result.get('description', ''))
            if snippet and args.include_preview:
                formatter.info(f"    {snippet}")
            
            # Tags
            if result.get('tags') and len(result['tags']) > 0:
                tag_str = ', '.join(result['tags'][:3])
                if len(result['tags']) > 3:
                    tag_str += f" +{len(result['tags']) - 3} more"
                formatter.info(f"    🏷️ {tag_str}")
            
            print()  # Add spacing between results
    
    def _show_detailed_results(self, formatter: TerminalFormatter, results: List[Dict[str, Any]], args):
        """Show detailed search results"""
        formatter.header(f"Detailed Search Results ({len(results)} found)", level=2)
        
        for result in results:
            formatter.header(f"{result['title']} (ID: {result['id']})", level=3)
            
            # Basic info
            info = {
                'Type': result['type'].title(),
                'Score': f"{result['relevance_score']:.2f}"
            }
            
            if result.get('content_type'):
                info['Content Type'] = result['content_type'].title()
            if result.get('author'):
                info['Author'] = result['author']
            if result.get('difficulty'):
                info['Difficulty'] = result['difficulty'].title()
            if result.get('status'):
                info['Status'] = result['status'].title()
            if result.get('created'):
                info['Created'] = result['created'][:10]
            
            formatter.key_value_pairs(info, indent=1)
            
            # Description
            if result.get('description'):
                formatter.info(f"  Description: {result['description']}")
            
            # Search snippet
            if result.get('search_snippet') and result['search_snippet'] != result.get('description', ''):
                formatter.info(f"  Match: {result['search_snippet']}")
            
            # Tags
            if result.get('tags'):
                formatter.info(f"  Tags: {', '.join(result['tags'])}")
            
            # Additional metrics
            metrics = []
            if result.get('score'):
                metrics.append(f"Rating: {result['score']:.1f}")
            if result.get('views'):
                metrics.append(f"Views: {result['views']}")
            if result.get('popularity'):
                metrics.append(f"Popularity: {result['popularity']}")
            if result.get('completion_rate'):
                metrics.append(f"Completion: {result['completion_rate']}%")
            
            if metrics:
                formatter.info(f"  Metrics: {' | '.join(metrics)}")
            
            print()
    
    def _show_search_summary(self, formatter: TerminalFormatter, results: List[Dict[str, Any]], args):
        """Show search results summary"""
        formatter.header(f"Search Summary ({len(results)} results)", level=2)
        
        # Results by type
        type_counts = {}
        for result in results:
            result_type = result['type']
            type_counts[result_type] = type_counts.get(result_type, 0) + 1
        
        formatter.info("Results by type:")
        for result_type, count in type_counts.items():
            formatter.info(f"  {result_type.title()}: {count}")
        
        # Top results
        formatter.header("Top 5 Results", level=3)
        for i, result in enumerate(results[:5], 1):
            type_icon = {'curriculum': '📚', 'content': '📄', 'user': '👤'}.get(result['type'], '📄')
            score_text = f" ({result['relevance_score']:.1f})" if args.sort == 'relevance' else ""
            formatter.info(f"  {i}. {type_icon} {result['title']}{score_text}")


class SavedSearchCommand(BaseCommand):
    """Manage saved searches"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="saved-search",
            description="Manage saved searches",
            category=CommandCategory.SYSTEM,
            aliases=["saved-searches", "search-saved"],
            examples=[
                "saved-search list",
                "saved-search run my-search",
                "saved-search delete old-search",
                "saved-search show my-search --details"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="Manage saved searches"
        )
        
        # Subcommands
        subcommands = parser.add_subparsers(dest='action', help='Saved search actions')
        
        # List saved searches
        list_parser = subcommands.add_parser('list', help='List saved searches')
        list_parser.add_argument('--format', choices=['table', 'json'], default='table')
        
        # Run saved search
        run_parser = subcommands.add_parser('run', help='Run a saved search')
        run_parser.add_argument('name', help='Saved search name')
        run_parser.add_argument('--format', choices=['list', 'detailed', 'json'], default='list')
        run_parser.add_argument('--limit', type=int, help='Override result limit')
        
        # Show saved search details
        show_parser = subcommands.add_parser('show', help='Show saved search details')
        show_parser.add_argument('name', help='Saved search name')
        show_parser.add_argument('--details', action='store_true', help='Show full details')
        
        # Delete saved search
        delete_parser = subcommands.add_parser('delete', help='Delete a saved search')
        delete_parser.add_argument('name', help='Saved search name')
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            if not parsed_args.action:
                return CommandResult(
                    success=False,
                    message="Please specify an action: list, run, show, or delete"
                )
            
            if parsed_args.action == 'list':
                return await self._list_saved_searches(context, parsed_args)
            elif parsed_args.action == 'run':
                return await self._run_saved_search(context, parsed_args)
            elif parsed_args.action == 'show':
                return await self._show_saved_search(context, parsed_args)
            elif parsed_args.action == 'delete':
                return await self._delete_saved_search(context, parsed_args)
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Saved search operation failed: {e}",
                error=e
            )
    
    async def _list_saved_searches(self, context, args) -> CommandResult:
        """List all saved searches"""
        # Mock data - replace with actual database query
        saved_searches = [
            {
                'name': 'python-basics',
                'query': 'python basics',
                'type': 'content',
                'created': '2024-01-15T10:30:00',
                'last_used': '2024-01-20T14:22:00',
                'use_count': 12
            },
            {
                'name': 'web-development',
                'query': 'web development',
                'type': 'all',
                'created': '2024-01-18T09:15:00',
                'last_used': '2024-01-22T11:45:00',
                'use_count': 8
            },
            {
                'name': 'advanced-topics',
                'query': 'advanced',
                'type': 'curriculum',
                'difficulty': 'advanced',
                'created': '2024-01-20T16:20:00',
                'last_used': '2024-01-21T10:30:00',
                'use_count': 3
            }
        ]
        
        if not saved_searches:
            return CommandResult(
                success=True,
                message="No saved searches found"
            )
        
        if args.format == 'json':
            output = json.dumps(saved_searches, indent=2, default=str)
            print(output)
        else:
            context.formatter.header(f"Saved Searches ({len(saved_searches)})", level=2)
            
            table_data = []
            for search in saved_searches:
                table_data.append({
                    'Name': search['name'],
                    'Query': search['query'][:30] + '...' if len(search['query']) > 30 else search['query'],
                    'Type': search.get('type', 'all').title(),
                    'Used': search['use_count'],
                    'Last Used': search['last_used'][:10]
                })
            
            context.formatter.table(table_data)
        
        return CommandResult(
            success=True,
            message=f"Found {len(saved_searches)} saved search(es)",
            data={'saved_searches': saved_searches}
        )
    
    async def _run_saved_search(self, context, args) -> CommandResult:
        """Run a saved search"""
        # Mock implementation - find saved search and execute it
        saved_search = await self._find_saved_search(context, args.name)
        
        if not saved_search:
            return CommandResult(
                success=False,
                message=f"Saved search '{args.name}' not found"
            )
        
        context.formatter.info(f"Running saved search: {saved_search['name']}")
        context.formatter.info(f"Query: {saved_search['query']}")
        
        # Execute the search using the SearchCommand
        search_command = SearchCommand()
        
        # Build arguments from saved search
        search_args = [saved_search['query']]
        
        if saved_search.get('type') != 'all':
            search_args.extend(['--type', saved_search['type']])
        
        for key, value in saved_search.get('filters', {}).items():
            if value:
                if key == 'tags' and isinstance(value, list):
                    for tag in value:
                        search_args.extend(['--tag', tag])
                else:
                    search_args.extend([f'--{key.replace("_", "-")}', str(value)])
        
        for key, value in saved_search.get('options', {}).items():
            if value:
                search_args.append(f'--{key.replace("_", "-")}')
        
        # Add format and limit
        search_args.extend(['--format', args.format])
        if args.limit:
            search_args.extend(['--limit', str(args.limit)])
        
        # Execute search
        result = await search_command.execute(context, search_args)
        
        # Update usage statistics
        await self._update_search_usage(context, args.name)
        
        return result
    
    async def _show_saved_search(self, context, args) -> CommandResult:
        """Show details of a saved search"""
        saved_search = await self._find_saved_search(context, args.name)
        
        if not saved_search:
            return CommandResult(
                success=False,
                message=f"Saved search '{args.name}' not found"
            )
        
        context.formatter.header(f"Saved Search: {saved_search['name']}", level=2)
        
        # Basic information
        basic_info = {
            'Name': saved_search['name'],
            'Query': saved_search['query'],
            'Type': saved_search.get('type', 'all').title(),
            'Created': saved_search['created'][:16],
            'Last Used': saved_search.get('last_used', 'Never')[:16],
            'Use Count': saved_search.get('use_count', 0)
        }
        context.formatter.key_value_pairs(basic_info)
        
        # Filters
        if args.details and saved_search.get('filters'):
            context.formatter.header("Filters", level=3)
            filters = {k: v for k, v in saved_search['filters'].items() if v}
            if filters:
                context.formatter.key_value_pairs(filters, indent=1)
            else:
                context.formatter.info("  No filters applied")
        
        # Options
        if args.details and saved_search.get('options'):
            context.formatter.header("Options", level=3)
            options = {k.replace('_', ' ').title(): v for k, v in saved_search['options'].items() if v}
            if options:
                context.formatter.key_value_pairs(options, indent=1)
            else:
                context.formatter.info("  No special options")
        
        return CommandResult(
            success=True,
            data={'saved_search': saved_search}
        )
    
    async def _delete_saved_search(self, context, args) -> CommandResult:
        """Delete a saved search"""
        saved_search = await self._find_saved_search(context, args.name)
        
        if not saved_search:
            return CommandResult(
                success=False,
                message=f"Saved search '{args.name}' not found"
            )
        
        # Confirm deletion
        if not args.force:
            if not self.confirm_action(
                f"Delete saved search '{args.name}'?", 
                default=False
            ):
                return CommandResult(
                    success=False,
                    message="Deletion cancelled"
                )
        
        # Delete the search
        await self._remove_saved_search(context, args.name)
        
        context.formatter.success(f"Saved search '{args.name}' deleted successfully")
        
        return CommandResult(
            success=True,
            message=f"Saved search '{args.name}' deleted"
        )
    
    async def _find_saved_search(self, context, name: str) -> Optional[Dict[str, Any]]:
        """Find a saved search by name"""
        # Mock implementation - replace with actual database query
        saved_searches = {
            'python-basics': {
                'name': 'python-basics',
                'query': 'python basics',
                'type': 'content',
                'created': '2024-01-15T10:30:00',
                'last_used': '2024-01-20T14:22:00',
                'use_count': 12,
                'filters': {
                    'difficulty': 'beginner',
                    'tags': ['python']
                },
                'options': {
                    'fuzzy': True
                }
            }
        }
        
        return saved_searches.get(name)
    
    async def _update_search_usage(self, context, name: str):
        """Update usage statistics for saved search"""
        # Mock implementation - replace with actual database update
        pass
    
    async def _remove_saved_search(self, context, name: str):
        """Remove saved search from storage"""
        # Mock implementation - replace with actual database deletion
        pass


class SearchAnalyticsCommand(BaseCommand):
    """View search analytics and popular searches"""
    
    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            name="search-analytics",
            description="View search analytics and trends",
            category=CommandCategory.SYSTEM,
            aliases=["search-stats", "analytics-search"],
            examples=[
                "search-analytics",
                "search-analytics --period 7d",
                "search-analytics --type popular-queries",
                "search-analytics --export csv"
            ]
        )
    
    def setup_parser(self, subparsers):
        parser = self.create_subparser(
            subparsers,
            help="View search analytics and trends"
        )
        
        # Analytics type
        parser.add_argument(
            '--type',
            choices=['overview', 'popular-queries', 'no-results', 'user-behavior', 'performance'],
            default='overview',
            help='Type of analytics to show'
        )
        
        # Time period
        parser.add_argument(
            '--period',
            choices=['1d', '7d', '30d', '90d'],
            default='7d',
            help='Time period for analytics'
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
            choices=['csv', 'json'],
            help='Export analytics data'
        )
        parser.add_argument(
            '--output-file',
            help='Output file for export'
        )
        
        return parser
    
    async def execute(self, context, args: List[str]) -> CommandResult:
        try:
            parsed_args = self.parse_args(args)
            
            # Generate analytics based on type
            if parsed_args.type == 'overview':
                analytics_data = await self._generate_overview_analytics(context, parsed_args)
            elif parsed_args.type == 'popular-queries':
                analytics_data = await self._generate_popular_queries_analytics(context, parsed_args)
            elif parsed_args.type == 'no-results':
                analytics_data = await self._generate_no_results_analytics(context, parsed_args)
            elif parsed_args.type == 'user-behavior':
                analytics_data = await self._generate_user_behavior_analytics(context, parsed_args)
            elif parsed_args.type == 'performance':
                analytics_data = await self._generate_performance_analytics(context, parsed_args)
            
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
                message=f"{parsed_args.type.replace('-', ' ').title()} analytics generated",
                data={'analytics': analytics_data}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to generate search analytics: {e}",
                error=e
            )
    
    async def _generate_overview_analytics(self, context, args) -> Dict[str, Any]:
        """Generate overview search analytics"""
        # Mock implementation - replace with actual analytics queries
        period_days = int(args.period.rstrip('d'))
        
        return {
            'report_type': 'overview',
            'period': args.period,
            'generated_at': datetime.now().isoformat(),
            'total_searches': 2847,
            'unique_queries': 1234,
            'average_results_per_search': 12.3,
            'searches_with_no_results': 142,
            'no_results_rate': 5.0,
            'popular_search_types': {
                'content': 1521,
                'curriculum': 823,
                'all': 503
            },
            'top_queries': [
                {'query': 'python basics', 'count': 89, 'avg_results': 15.2},
                {'query': 'web development', 'count': 76, 'avg_results': 22.1},
                {'query': 'javascript', 'count': 54, 'avg_results': 18.7},
                {'query': 'data science', 'count': 48, 'avg_results': 11.3},
                {'query': 'machine learning', 'count': 42, 'avg_results': 8.9}
            ],
            'search_trends': {
                'labels': [f'Day {i}' for i in range(1, period_days + 1)],
                'searches': [45, 52, 48, 61, 58, 67, 71] if period_days == 7 else list(range(30, 80, 2))[:period_days]
            }
        }
    
    async def _generate_popular_queries_analytics(self, context, args) -> Dict[str, Any]:
        """Generate popular queries analytics"""
        return {
            'report_type': 'popular_queries',
            'period': args.period,
            'generated_at': datetime.now().isoformat(),
            'top_queries_by_volume': [
                {'query': 'python basics', 'searches': 89, 'unique_users': 67, 'avg_results': 15.2},
                {'query': 'web development', 'searches': 76, 'unique_users': 58, 'avg_results': 22.1},
                {'query': 'javascript fundamentals', 'searches': 54, 'unique_users': 41, 'avg_results': 18.7},
                {'query': 'data science introduction', 'searches': 48, 'unique_users': 36, 'avg_results': 11.3},
                {'query': 'machine learning basics', 'searches': 42, 'unique_users': 31, 'avg_results': 8.9}
            ],
            'trending_queries': [
                {'query': 'react hooks', 'growth_rate': 145.3, 'searches': 23},
                {'query': 'python async', 'growth_rate': 89.2, 'searches': 18},
                {'query': 'docker containers', 'growth_rate': 76.8, 'searches': 15}
            ],
            'query_categories': {
                'programming_languages': 45.2,
                'frameworks': 23.1,
                'databases': 12.7,
                'tools': 11.3,
                'concepts': 7.7
            }
        }
    
    async def _generate_no_results_analytics(self, context, args) -> Dict[str, Any]:
        """Generate no results analytics"""
        return {
            'report_type': 'no_results',
            'period': args.period,
            'generated_at': datetime.now().isoformat(),
            'total_no_result_searches': 142,
            'no_results_rate': 5.0,
            'common_no_result_queries': [
                {'query': 'blockchain development', 'count': 12, 'suggested': 'blockchain basics'},
                {'query': 'quantum computing', 'count': 8, 'suggested': 'computer science'},
                {'query': 'advanced ai', 'count': 7, 'suggested': 'artificial intelligence'},
                {'query': 'rust programming', 'count': 6, 'suggested': 'programming languages'},
                {'query': 'kubernetes advanced', 'count': 5, 'suggested': 'kubernetes basics'}
            ],
            'improvement_opportunities': [
                'Add more blockchain-related content',
                'Create quantum computing curriculum',
                'Expand AI/ML advanced topics',
                'Add Rust programming courses',
                'Develop advanced Kubernetes content'
            ],
            'query_patterns': {
                'too_specific': 42.3,
                'typos': 28.9,
                'unknown_topics': 18.3,
                'wrong_terminology': 10.5
            }
        }
    
    async def _generate_user_behavior_analytics(self, context, args) -> Dict[str, Any]:
        """Generate user behavior analytics"""
        return {
            'report_type': 'user_behavior',
            'period': args.period,
            'generated_at': datetime.now().isoformat(),
            'search_patterns': {
                'avg_searches_per_user': 3.2,
                'avg_query_length': 2.8,
                'refinement_rate': 23.4,
                'click_through_rate': 67.8
            },
            'popular_filters': [
                {'filter': 'difficulty:beginner', 'usage': 34.2},
                {'filter': 'type:content', 'usage': 28.9},
                {'filter': 'status:published', 'usage': 19.7},
                {'filter': 'tag:python', 'usage': 15.3}
            ],
            'search_sequences': [
                {'sequence': 'python -> python basics -> python variables', 'frequency': 89},
                {'sequence': 'web -> web development -> html css', 'frequency': 76},
                {'sequence': 'javascript -> js fundamentals -> react', 'frequency': 54}
            ],
            'time_patterns': {
                'peak_hours': [9, 10, 11, 14, 15, 16],
                'peak_days': ['Monday', 'Tuesday', 'Wednesday'],
                'weekend_usage': 12.3
            }
        }
    
    async def _generate_performance_analytics(self, context, args) -> Dict[str, Any]:
        """Generate search performance analytics"""
        return {
            'report_type': 'performance',
            'period': args.period,
            'generated_at': datetime.now().isoformat(),
            'response_times': {
                'avg_response_time_ms': 145.3,
                'median_response_time_ms': 98.7,
                'p95_response_time_ms': 287.4,
                'p99_response_time_ms': 456.8
            },
            'search_volume': {
                'peak_qps': 23.4,
                'avg_qps': 8.7,
                'total_queries': 2847
            },
            'result_quality': {
                'avg_relevance_score': 7.8,
                'queries_with_high_relevance': 78.9,
                'user_satisfaction_rate': 82.3
            },
            'system_usage': {
                'cache_hit_rate': 67.4,
                'index_size_mb': 1247.8,
                'memory_usage_mb': 234.5
            }
        }
    
    def _show_analytics_report(self, formatter: TerminalFormatter, data: Dict[str, Any], report_type: str):
        """Show analytics report"""
        formatter.header(f"{report_type.replace('_', ' ').title()} Analytics", level=1)
        formatter.info(f"Period: {data['period']} | Generated: {data['generated_at'][:16]}")
        
        if report_type == 'overview':
            self._show_overview_report(formatter, data)
        elif report_type == 'popular_queries':
            self._show_popular_queries_report(formatter, data)
        elif report_type == 'no_results':
            self._show_no_results_report(formatter, data)
        elif report_type == 'user_behavior':
            self._show_user_behavior_report(formatter, data)
        elif report_type == 'performance':
            self._show_performance_report(formatter, data)
    
    def _show_overview_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show overview analytics report"""
        # Key metrics
        formatter.header("Key Metrics", level=2)
        metrics = {
            'Total Searches': data['total_searches'],
            'Unique Queries': data['unique_queries'],
            'Avg Results per Search': f"{data['average_results_per_search']:.1f}",
            'No Results Rate': f"{data['no_results_rate']:.1f}% ({data['searches_with_no_results']} searches)"
        }
        formatter.key_value_pairs(metrics)
        
        # Search types
        formatter.header("Popular Search Types", level=2)
        total_type_searches = sum(data['popular_search_types'].values())
        for search_type, count in data['popular_search_types'].items():
            percentage = (count / total_type_searches) * 100
            bar_length = int((count / max(data['popular_search_types'].values())) * 30)
            bar = "█" * bar_length
            formatter.info(f"{search_type.title():10} {bar} {count} ({percentage:.1f}%)")
        
        # Top queries
        formatter.header("Top Queries", level=2)
        query_data = []
        for query in data['top_queries']:
            query_data.append({
                'Query': query['query'],
                'Searches': query['count'],
                'Avg Results': f"{query['avg_results']:.1f}"
            })
        formatter.table(query_data)
    
    def _show_popular_queries_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show popular queries report"""
        # Top queries by volume
        formatter.header("Top Queries by Volume", level=2)
        query_data = []
        for query in data['top_queries_by_volume']:
            query_data.append({
                'Query': query['query'],
                'Searches': query['searches'],
                'Users': query['unique_users'],
                'Avg Results': f"{query['avg_results']:.1f}"
            })
        formatter.table(query_data)
        
        # Trending queries
        if data.get('trending_queries'):
            formatter.header("Trending Queries", level=2)
            trending_data = []
            for query in data['trending_queries']:
                trending_data.append({
                    'Query': query['query'],
                    'Growth': f"+{query['growth_rate']:.1f}%",
                    'Searches': query['searches']
                })
            formatter.table(trending_data)
    
    def _show_no_results_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show no results analytics report"""
        formatter.info(f"No Results Rate: {data['no_results_rate']:.1f}% ({data['total_no_result_searches']} searches)")
        
        # Common no-result queries
        formatter.header("Common No-Result Queries", level=2)
        no_result_data = []
        for query in data['common_no_result_queries']:
            no_result_data.append({
                'Query': query['query'],
                'Count': query['count'],
                'Suggestion': query.get('suggested', 'None')
            })
        formatter.table(no_result_data)
        
        # Improvement opportunities
        if data.get('improvement_opportunities'):
            formatter.header("Content Gaps", level=2)
            for i, opportunity in enumerate(data['improvement_opportunities'], 1):
                formatter.info(f"  {i}. {opportunity}")
    
    def _show_user_behavior_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show user behavior report"""
        # Search patterns
        formatter.header("Search Patterns", level=2)
        patterns = data['search_patterns']
        formatter.key_value_pairs({
            'Avg Searches per User': f"{patterns['avg_searches_per_user']:.1f}",
            'Avg Query Length': f"{patterns['avg_query_length']:.1f} words",
            'Refinement Rate': f"{patterns['refinement_rate']:.1f}%",
            'Click-through Rate': f"{patterns['click_through_rate']:.1f}%"
        })
        
        # Popular filters
        formatter.header("Popular Filters", level=2)
        for filter_info in data['popular_filters']:
            usage_bar = int((filter_info['usage'] / 100) * 20)
            bar = "█" * usage_bar
            formatter.info(f"{filter_info['filter']:20} {bar} {filter_info['usage']:.1f}%")
    
    def _show_performance_report(self, formatter: TerminalFormatter, data: Dict[str, Any]):
        """Show performance analytics report"""
        # Response times
        formatter.header("Response Times", level=2)
        times = data['response_times']
        formatter.key_value_pairs({
            'Average': f"{times['avg_response_time_ms']:.1f}ms",
            'Median': f"{times['median_response_time_ms']:.1f}ms",
            '95th Percentile': f"{times['p95_response_time_ms']:.1f}ms",
            '99th Percentile': f"{times['p99_response_time_ms']:.1f}ms"
        })
        
        # Search volume
        formatter.header("Search Volume", level=2)
        volume = data['search_volume']
        formatter.key_value_pairs({
            'Peak QPS': f"{volume['peak_qps']:.1f}",
            'Average QPS': f"{volume['avg_qps']:.1f}",
            'Total Queries': volume['total_queries']
        })
        
        # Result quality
        formatter.header("Result Quality", level=2)
        quality = data['result_quality']
        formatter.key_value_pairs({
            'Avg Relevance Score': f"{quality['avg_relevance_score']:.1f}/10.0",
            'High Relevance Rate': f"{quality['queries_with_high_relevance']:.1f}%",
            'User Satisfaction': f"{quality['user_satisfaction_rate']:.1f}%"
        })
    
    def _show_analytics_charts(self, formatter: TerminalFormatter, data: Dict[str, Any], report_type: str):
        """Show analytics as charts"""
        formatter.header(f"{report_type.replace('_', ' ').title()} Charts", level=1)
        
        if report_type == 'overview' and 'search_trends' in data:
            trend = data['search_trends']
            formatter.header("Search Volume Trend", level=2)
            
            max_value = max(trend['searches'])
            for label, value in zip(trend['labels'], trend['searches']):
                bar_length = int((value / max_value) * 40)
                bar = "█" * bar_length
                formatter.info(f"{label:8} {bar} {value}")
    
    async def _export_analytics(self, context, data: Dict[str, Any], export_format: str,
                               output_file: Optional[str], report_type: str) -> str:
        """Export analytics to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"search_analytics_{report_type}_{timestamp}.{export_format}"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if export_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif export_format == 'csv':
            # Convert to CSV based on report type
            import csv
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                if report_type == 'popular_queries':
                    writer.writerow(['Query', 'Searches', 'Unique Users', 'Avg Results'])
                    for query in data.get('top_queries_by_volume', []):
                        writer.writerow([query['query'], query['searches'], 
                                       query['unique_users'], query['avg_results']])
        
        return str(output_path)
