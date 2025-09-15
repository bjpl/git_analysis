#!/usr/bin/env python3
"""
Notes Manager - Comprehensive note management system for the curriculum
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.console import Console
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown as RichMarkdown

console = Console()

class NotesManager:
    """Manages all note-taking operations for the curriculum"""
    
    def __init__(self, db_path: str = "curriculum.db"):
        self.db_path = db_path
        self.notes_dir = Path("notes")
        self.notes_dir.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize notes table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create dedicated notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    lesson_id INTEGER,
                    module_name TEXT,
                    topic TEXT,
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
                )
            """)
            
            # Create notes index for faster searching
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_user 
                ON notes(user_id, created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_lesson 
                ON notes(lesson_id, user_id)
            """)
            
            # Ensure progress table exists and has notes column
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='progress'
            """)
            if cursor.fetchone():
                # Table exists, check for notes column
                cursor.execute("PRAGMA table_info(progress)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'notes' not in columns:
                    cursor.execute("ALTER TABLE progress ADD COLUMN notes TEXT")
            
            conn.commit()
    
    def save_note(self, user_id: int, lesson_id: Optional[int], 
                  content: str, module_name: str = "", 
                  topic: str = "", tags: List[str] = None) -> int:
        """Save a new note to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            tags_str = json.dumps(tags) if tags else "[]"
            
            cursor.execute("""
                INSERT INTO notes (user_id, lesson_id, module_name, topic, content, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, lesson_id, module_name, topic, content, tags_str))
            
            note_id = cursor.lastrowid
            
            # Also update progress table if lesson_id exists
            if lesson_id:
                cursor.execute("""
                    UPDATE progress 
                    SET notes = COALESCE(notes || '\n---\n' || ?, ?)
                    WHERE user_id = ? AND lesson_id = ?
                """, (content, content, user_id, lesson_id))
            
            conn.commit()
            return note_id
    
    def get_notes(self, user_id: int, lesson_id: Optional[int] = None,
                  module_name: Optional[str] = None, 
                  search_term: Optional[str] = None) -> List[Dict]:
        """Retrieve notes with optional filters"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT n.id, n.lesson_id, n.module_name, n.topic, 
                       n.content, n.tags, n.created_at, n.updated_at, 
                       n.is_favorite, l.title as lesson_title
                FROM notes n
                LEFT JOIN lessons l ON n.lesson_id = l.id
                WHERE n.user_id = ?
            """
            params = [user_id]
            
            if lesson_id:
                query += " AND n.lesson_id = ?"
                params.append(lesson_id)
            
            if module_name:
                query += " AND n.module_name = ?"
                params.append(module_name)
            
            if search_term:
                query += " AND (n.content LIKE ? OR n.topic LIKE ? OR n.tags LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            query += " ORDER BY n.created_at DESC"
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            notes = []
            
            for row in cursor.fetchall():
                note = dict(zip(columns, row))
                note['tags'] = json.loads(note['tags']) if note['tags'] else []
                notes.append(note)
            
            return notes
    
    def update_note(self, note_id: int, content: str, 
                    tags: List[str] = None) -> bool:
        """Update an existing note"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            tags_str = json.dumps(tags) if tags else None
            
            cursor.execute("""
                UPDATE notes 
                SET content = ?, tags = COALESCE(?, tags), 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (content, tags_str, note_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def toggle_favorite(self, note_id: int) -> bool:
        """Toggle favorite status of a note"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notes 
                SET is_favorite = NOT is_favorite,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (note_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def export_notes(self, user_id: int, format: str = "markdown",
                     output_dir: Optional[str] = None) -> str:
        """Export notes to file"""
        notes = self.get_notes(user_id)
        
        if not notes:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(output_dir or "notes/exports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "markdown":
            filename = output_dir / f"notes_export_{timestamp}.md"
            content = self._format_notes_markdown(notes)
            
        elif format == "html":
            filename = output_dir / f"notes_export_{timestamp}.html"
            md_content = self._format_notes_markdown(notes)
            content = self._markdown_to_html(md_content)
            
        elif format == "json":
            filename = output_dir / f"notes_export_{timestamp}.json"
            content = json.dumps(notes, indent=2, default=str)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filename)
    
    def _format_notes_markdown(self, notes: List[Dict]) -> str:
        """Format notes as markdown"""
        lines = ["# 📚 Learning Notes\n"]
        lines.append(f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        
        # Group by module
        modules = {}
        for note in notes:
            module = note.get('module_name', 'General')
            if module not in modules:
                modules[module] = []
            modules[module].append(note)
        
        for module, module_notes in modules.items():
            lines.append(f"## 📂 {module}\n")
            
            for note in module_notes:
                lines.append(f"### 📝 {note.get('topic', 'Note')}")
                
                if note.get('lesson_title'):
                    lines.append(f"*Lesson: {note['lesson_title']}*")
                
                lines.append(f"*Created: {note['created_at']}*")
                
                if note.get('is_favorite'):
                    lines.append("⭐ **Favorited**")
                
                if note.get('tags'):
                    tags_str = " ".join([f"`{tag}`" for tag in note['tags']])
                    lines.append(f"Tags: {tags_str}")
                
                lines.append(f"\n{note['content']}\n")
                lines.append("---\n")
        
        return "\n".join(lines)
    
    def _markdown_to_html(self, md_content: str) -> str:
        """Convert markdown to HTML with styling"""
        if HAS_MARKDOWN:
            html_body = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        else:
            # Basic conversion without markdown library
            html_body = md_content.replace('\n', '<br>\n')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Learning Notes</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #666;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 30px 0;
        }}
        em {{ color: #666; }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
        return html
    
    def get_statistics(self, user_id: int) -> Dict:
        """Get note-taking statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total notes
            cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,))
            total_notes = cursor.fetchone()[0]
            
            # Notes by module
            cursor.execute("""
                SELECT module_name, COUNT(*) as count
                FROM notes 
                WHERE user_id = ?
                GROUP BY module_name
                ORDER BY count DESC
            """, (user_id,))
            by_module = dict(cursor.fetchall())
            
            # Recent notes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM notes 
                WHERE user_id = ? 
                AND datetime(created_at) > datetime('now', '-7 days')
            """, (user_id,))
            recent_notes = cursor.fetchone()[0]
            
            # Favorite notes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM notes 
                WHERE user_id = ? AND is_favorite = 1
            """, (user_id,))
            favorites = cursor.fetchone()[0]
            
            return {
                'total_notes': total_notes,
                'by_module': by_module,
                'recent_notes': recent_notes,
                'favorites': favorites
            }
    
    def display_notes(self, notes: List[Dict], title: str = "Notes"):
        """Display notes in a formatted table"""
        if not notes:
            console.print("[yellow]No notes found.[/yellow]")
            return
        
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Module", style="magenta")
        table.add_column("Topic", style="green")
        table.add_column("Content", style="white", overflow="fold")
        table.add_column("Tags", style="blue")
        table.add_column("Created", style="dim")
        table.add_column("⭐", justify="center", width=3)
        
        for note in notes[:20]:  # Show max 20 notes in table
            content_preview = note['content'][:100] + "..." if len(note['content']) > 100 else note['content']
            tags_str = ", ".join(note.get('tags', []))[:30]
            created = datetime.fromisoformat(note['created_at']).strftime("%m/%d %H:%M")
            fav = "⭐" if note.get('is_favorite') else ""
            
            table.add_row(
                str(note['id']),
                note.get('module_name', 'General')[:20],
                note.get('topic', 'Note')[:30],
                content_preview,
                tags_str,
                created,
                fav
            )
        
        console.print(table)
        
        if len(notes) > 20:
            console.print(f"\n[dim]Showing 20 of {len(notes)} notes. Use filters to narrow results.[/dim]")
    
    def cleanup_orphaned_notes(self) -> int:
        """Remove notes with invalid references"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find orphaned notes (lessons that don't exist)
            cursor.execute("""
                DELETE FROM notes 
                WHERE lesson_id IS NOT NULL 
                AND lesson_id NOT IN (SELECT id FROM lessons)
            """)
            
            deleted = cursor.rowcount
            conn.commit()
            
            return deleted
    
    def migrate_old_notes(self) -> int:
        """Migrate notes from progress table to notes table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all notes from progress table
            cursor.execute("""
                SELECT p.user_id, p.lesson_id, p.notes, l.title
                FROM progress p
                LEFT JOIN lessons l ON p.lesson_id = l.id
                WHERE p.notes IS NOT NULL AND p.notes != ''
            """)
            
            migrated = 0
            for row in cursor.fetchall():
                user_id, lesson_id, notes_content, lesson_title = row
                
                # Use lesson title or default module name
                module_name = "General"
                if lesson_title:
                    # Extract module from title if possible
                    if ':' in lesson_title:
                        module_name = lesson_title.split(':')[0].strip()
                    elif '-' in lesson_title:
                        module_name = lesson_title.split('-')[0].strip()
                
                # Check if already migrated
                cursor.execute("""
                    SELECT COUNT(*) FROM notes 
                    WHERE user_id = ? AND lesson_id = ? AND content = ?
                """, (user_id, lesson_id, notes_content))
                
                if cursor.fetchone()[0] == 0:
                    # Migrate the note
                    cursor.execute("""
                        INSERT INTO notes (user_id, lesson_id, module_name, topic, content)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, lesson_id, module_name, lesson_title or "Note", notes_content))
                    migrated += 1
            
            conn.commit()
            return migrated


# CLI Integration Functions
def integrate_with_cli(cli_instance):
    """Integrate notes manager with the CLI"""
    notes_mgr = NotesManager()
    
    # Add notes commands to CLI
    def cmd_note_add(args):
        """Add a new note"""
        content = input("Enter note content (press Enter twice to finish):\n")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        content = "\n".join([content] + lines)
        
        topic = input("Topic (optional): ").strip() or "General Note"
        tags_input = input("Tags (comma-separated, optional): ").strip()
        tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
        
        # Get current context from CLI
        user_id = getattr(cli_instance, 'current_user_id', 1)
        lesson_id = getattr(cli_instance, 'current_lesson_id', None)
        module_name = getattr(cli_instance, 'current_module', 'General')
        
        note_id = notes_mgr.save_note(
            user_id, lesson_id, content, 
            module_name, topic, tags
        )
        
        console.print(f"[green]✓ Note saved with ID: {note_id}[/green]")
    
    def cmd_note_list(args):
        """List notes with optional filters"""
        user_id = getattr(cli_instance, 'current_user_id', 1)
        
        # Handle args being a dict, string, or None
        if isinstance(args, dict):
            search = args.get('search')
            module = args.get('module')
        else:
            search = None
            module = None
        
        notes = notes_mgr.get_notes(user_id, module_name=module, search_term=search)
        notes_mgr.display_notes(notes, title="Your Notes")
    
    def cmd_note_export(args):
        """Export notes to file"""
        user_id = getattr(cli_instance, 'current_user_id', 1)
        
        # Handle args being a dict, string, or None
        if isinstance(args, dict):
            format = args.get('format', 'markdown')
        else:
            format = 'markdown'
        
        filename = notes_mgr.export_notes(user_id, format)
        if filename:
            console.print(f"[green]✓ Notes exported to: {filename}[/green]")
        else:
            console.print("[yellow]No notes to export.[/yellow]")
    
    def cmd_note_stats(args):
        """Show note statistics"""
        user_id = getattr(cli_instance, 'current_user_id', 1)
        stats = notes_mgr.get_statistics(user_id)
        
        panel = Panel(
            f"""[bold cyan]📊 Note Statistics[/bold cyan]
            
📝 Total Notes: [bold]{stats['total_notes']}[/bold]
⭐ Favorites: [bold]{stats['favorites']}[/bold]
📅 Recent (7 days): [bold]{stats['recent_notes']}[/bold]

[bold]Notes by Module:[/bold]
{chr(10).join([f"  • {m}: {c}" for m, c in stats['by_module'].items()])}
            """,
            expand=False,
            border_style="cyan"
        )
        console.print(panel)
    
    def cmd_note_cleanup(args):
        """Clean up orphaned notes and migrate old ones"""
        # Migrate old notes
        migrated = notes_mgr.migrate_old_notes()
        if migrated > 0:
            console.print(f"[green]✓ Migrated {migrated} notes from old system[/green]")
        
        # Clean orphaned
        deleted = notes_mgr.cleanup_orphaned_notes()
        if deleted > 0:
            console.print(f"[yellow]⚠ Removed {deleted} orphaned notes[/yellow]")
        
        console.print("[green]✓ Notes cleanup complete[/green]")
    
    # Register commands with CLI
    cli_commands = {
        'note': cmd_note_add,
        'notes': cmd_note_list,
        'note-export': cmd_note_export,
        'note-stats': cmd_note_stats,
        'note-cleanup': cmd_note_cleanup
    }
    
    return cli_commands


if __name__ == "__main__":
    # Standalone testing
    mgr = NotesManager()
    
    # Initialize and migrate
    console.print("[bold]Initializing Notes System...[/bold]")
    
    # Clean up and migrate
    migrated = mgr.migrate_old_notes()
    deleted = mgr.cleanup_orphaned_notes()
    
    console.print(f"[green]✓ System initialized[/green]")
    if migrated:
        console.print(f"  • Migrated {migrated} notes")
    if deleted:
        console.print(f"  • Cleaned {deleted} orphaned notes")
    
    # Show stats
    stats = mgr.get_statistics(1)
    console.print(f"\n[bold]Current Statistics:[/bold]")
    console.print(f"  • Total notes: {stats['total_notes']}")
    console.print(f"  • Favorites: {stats['favorites']}")
    console.print(f"  • Recent notes: {stats['recent_notes']}")