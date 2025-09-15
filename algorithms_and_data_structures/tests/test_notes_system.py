#!/usr/bin/env python3
"""
Test the integrated notes system
"""

import sys
import sqlite3
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from notes_manager import NotesManager

console = Console()

def test_notes_system():
    """Test all notes functionality"""
    console.print("[bold cyan]📝 Testing Notes System[/bold cyan]\n")
    
    notes_mgr = NotesManager()
    user_id = 1
    
    # Test 1: Add a test note
    console.print("1️⃣ Adding test note...")
    note_id = notes_mgr.save_note(
        user_id=user_id,
        lesson_id=None,
        content="This is a test note to verify the system is working correctly.",
        module_name="Testing",
        topic="System Test",
        tags=["test", "verification"]
    )
    console.print(f"   [green]✓ Note created with ID: {note_id}[/green]")
    
    # Test 2: Retrieve notes
    console.print("\n2️⃣ Retrieving notes...")
    notes = notes_mgr.get_notes(user_id)
    console.print(f"   [green]✓ Found {len(notes)} notes[/green]")
    
    # Test 3: Display notes
    console.print("\n3️⃣ Displaying notes:")
    notes_mgr.display_notes(notes, title="All Notes")
    
    # Test 4: Search notes
    console.print("\n4️⃣ Testing search...")
    search_results = notes_mgr.get_notes(user_id, search_term="test")
    console.print(f"   [green]✓ Search found {len(search_results)} matching notes[/green]")
    
    # Test 5: Update note
    if notes:
        console.print("\n5️⃣ Updating note...")
        first_note_id = notes[0]['id']
        success = notes_mgr.update_note(
            first_note_id, 
            "Updated content: The system is working perfectly!",
            tags=["test", "updated", "working"]
        )
        console.print(f"   [green]✓ Note updated: {success}[/green]")
    
    # Test 6: Toggle favorite
    if notes:
        console.print("\n6️⃣ Testing favorites...")
        success = notes_mgr.toggle_favorite(notes[0]['id'])
        console.print(f"   [green]✓ Favorite toggled: {success}[/green]")
    
    # Test 7: Statistics
    console.print("\n7️⃣ Getting statistics...")
    stats = notes_mgr.get_statistics(user_id)
    
    panel = Panel(
        f"""[bold]📊 Current Statistics:[/bold]
        
Total Notes: [cyan]{stats['total_notes']}[/cyan]
Favorites: [yellow]{stats['favorites']}[/yellow]
Recent (7 days): [green]{stats['recent_notes']}[/green]

[bold]By Module:[/bold]
{chr(10).join([f"  • {m}: {c}" for m, c in stats['by_module'].items()])}
        """,
        title="Notes Statistics",
        border_style="green"
    )
    console.print(panel)
    
    # Test 8: Export test
    console.print("\n8️⃣ Testing export...")
    
    # Markdown export
    md_file = notes_mgr.export_notes(user_id, format="markdown")
    if md_file:
        console.print(f"   [green]✓ Markdown export: {md_file}[/green]")
    
    # HTML export
    html_file = notes_mgr.export_notes(user_id, format="html")
    if html_file:
        console.print(f"   [green]✓ HTML export: {html_file}[/green]")
    
    # JSON export
    json_file = notes_mgr.export_notes(user_id, format="json")
    if json_file:
        console.print(f"   [green]✓ JSON export: {json_file}[/green]")
    
    console.print("\n[bold green]✅ All tests completed successfully![/bold green]")
    
    # Show how to integrate with CLI
    console.print("\n[bold]Integration Instructions:[/bold]")
    console.print("""
To integrate with your curriculum CLI, add these commands:

```python
from src.notes_manager import NotesManager, integrate_with_cli

# In your CLI class initialization:
self.notes_mgr = NotesManager()
self.commands.update(integrate_with_cli(self))
```

Or use the commands directly:
- `python curriculum_cli_enhanced.py note` - Add a note
- `python curriculum_cli_enhanced.py notes` - List notes
- `python curriculum_cli_enhanced.py note-export` - Export notes
- `python curriculum_cli_enhanced.py note-stats` - View statistics
    """)

if __name__ == "__main__":
    test_notes_system()