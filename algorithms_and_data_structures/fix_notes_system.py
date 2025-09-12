#!/usr/bin/env python3
"""
Fix and integrate the notes system with the curriculum CLI
"""

import sys
import sqlite3
from pathlib import Path
from rich.console import Console

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from notes_manager import NotesManager

console = Console()

def main():
    """Main function to fix the notes system"""
    console.print("[bold cyan]🔧 Fixing Notes System...[/bold cyan]\n")
    
    # Initialize notes manager
    notes_mgr = NotesManager()
    
    # Step 1: Initialize database tables
    console.print("1️⃣ Initializing database tables...")
    notes_mgr._init_database()
    console.print("   [green]✓ Database tables created/verified[/green]")
    
    # Step 2: Migrate existing notes
    console.print("\n2️⃣ Migrating existing notes from progress table...")
    migrated = notes_mgr.migrate_old_notes()
    if migrated > 0:
        console.print(f"   [green]✓ Migrated {migrated} notes[/green]")
    else:
        console.print("   [dim]No notes to migrate[/dim]")
    
    # Step 3: Import notes from claude_code_notes directory
    console.print("\n3️⃣ Importing notes from claude_code_notes directory...")
    notes_dir = Path("claude_code_notes")
    imported = 0
    
    if notes_dir.exists():
        for note_file in notes_dir.glob("*.md"):
            with open(note_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract topic from filename
            topic = note_file.stem.replace('_', ' ').title()
            
            # Save to database
            note_id = notes_mgr.save_note(
                user_id=1,  # Default user
                lesson_id=None,
                content=content,
                module_name="Imported",
                topic=topic,
                tags=["imported", "claude-code"]
            )
            imported += 1
            console.print(f"   [dim]Imported: {note_file.name}[/dim]")
    
    if imported > 0:
        console.print(f"   [green]✓ Imported {imported} notes from files[/green]")
    else:
        console.print("   [dim]No external notes to import[/dim]")
    
    # Step 4: Clean up orphaned notes
    console.print("\n4️⃣ Cleaning up orphaned notes...")
    deleted = notes_mgr.cleanup_orphaned_notes()
    if deleted > 0:
        console.print(f"   [yellow]⚠ Removed {deleted} orphaned notes[/yellow]")
    else:
        console.print("   [green]✓ No orphaned notes found[/green]")
    
    # Step 5: Display statistics
    console.print("\n5️⃣ Verifying system...")
    stats = notes_mgr.get_statistics(1)
    
    console.print("\n[bold]📊 Notes System Status:[/bold]")
    console.print(f"   • Total notes: [bold cyan]{stats['total_notes']}[/bold cyan]")
    console.print(f"   • Favorite notes: [bold yellow]{stats['favorites']}[/bold yellow]")
    console.print(f"   • Recent notes (7 days): [bold green]{stats['recent_notes']}[/bold green]")
    
    if stats['by_module']:
        console.print("\n   [bold]Notes by Module:[/bold]")
        for module, count in stats['by_module'].items():
            console.print(f"     • {module}: {count}")
    
    # Step 6: Export a backup
    console.print("\n6️⃣ Creating backup export...")
    if stats['total_notes'] > 0:
        export_file = notes_mgr.export_notes(1, format="markdown")
        if export_file:
            console.print(f"   [green]✓ Backup exported to: {export_file}[/green]")
    else:
        console.print("   [dim]No notes to export[/dim]")
    
    console.print("\n[bold green]✅ Notes system fixed and ready![/bold green]")
    console.print("\n[bold]Available commands in CLI:[/bold]")
    console.print("   • [cyan]note[/cyan] - Add a new note")
    console.print("   • [cyan]notes[/cyan] - List all notes")
    console.print("   • [cyan]note-export[/cyan] - Export notes to file")
    console.print("   • [cyan]note-stats[/cyan] - View note statistics")
    console.print("   • [cyan]note-cleanup[/cyan] - Clean up and organize notes")

if __name__ == "__main__":
    main()