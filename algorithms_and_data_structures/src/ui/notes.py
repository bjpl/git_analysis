#!/usr/bin/env python3
"""
Enhanced Note-Taking System with Rich Formatting
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from .formatter import TerminalFormatter, Color, Theme
from .navigation import NavigationController, MenuItem


class NoteType(Enum):
    """Types of notes"""
    CONCEPT = "concept"
    EXAMPLE = "example"
    QUESTION = "question"
    INSIGHT = "insight"
    TODO = "todo"
    REFERENCE = "reference"


class Priority(Enum):
    """Note priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class RichNote:
    """Enhanced note with rich formatting support"""
    id: str
    title: str
    content: str
    note_type: NoteType
    priority: Priority
    tags: List[str] = field(default_factory=list)
    topic: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    formatted_content: str = ""
    code_snippets: List[Dict[str, str]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    parent_note_id: Optional[str] = None
    child_note_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Process content after initialization"""
        if not self.formatted_content:
            self.formatted_content = self._format_content()
    
    def _format_content(self) -> str:
        """Apply rich formatting to content"""
        formatted = self.content
        
        # Process markdown-like formatting
        # Bold: **text** or __text__
        formatted = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', formatted)
        formatted = re.sub(r'__(.*?)__', r'\033[1m\1\033[0m', formatted)
        
        # Italic: *text* or _text_
        formatted = re.sub(r'\*(.*?)\*', r'\033[3m\1\033[0m', formatted)
        formatted = re.sub(r'_(.*?)_', r'\033[3m\1\033[0m', formatted)
        
        # Code: `code`
        formatted = re.sub(r'`(.*?)`', r'\033[93m\033[40m\1\033[0m', formatted)
        
        # Headers: # Header
        formatted = re.sub(r'^# (.*?)$', r'\033[1m\033[94m\1\033[0m', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^## (.*?)$', r'\033[1m\033[96m\1\033[0m', formatted, flags=re.MULTILINE)
        
        # Lists: - item or * item
        formatted = re.sub(r'^[\-\*] (.*?)$', r'\033[92m•\033[0m \1', formatted, flags=re.MULTILINE)
        
        # Numbered lists: 1. item
        formatted = re.sub(r'^(\d+)\. (.*?)$', r'\033[93m\1.\033[0m \2', formatted, flags=re.MULTILINE)
        
        return formatted


class NoteEditor:
    """Rich text editor for notes"""
    
    def __init__(self, formatter: TerminalFormatter):
        self.formatter = formatter
        self.current_note: Optional[RichNote] = None
        self.editing_mode = False
        self.cursor_position = 0
        
        # Editor commands
        self.commands = {
            '/bold': self._insert_bold,
            '/italic': self._insert_italic,
            '/code': self._insert_code,
            '/header': self._insert_header,
            '/list': self._insert_list,
            '/link': self._insert_link,
            '/save': self._save_note,
            '/cancel': self._cancel_edit,
            '/help': self._show_help
        }
    
    async def create_new_note(self, topic: str = "") -> Optional[RichNote]:
        """Create a new note with the editor"""
        # Clear screen
        print('\033[2J\033[H', end='')
        
        print(self.formatter.header("📝 Create New Note", level=1, style="boxed"))
        
        # Note metadata input
        note_data = await self._get_note_metadata(topic)
        if not note_data:
            return None
        
        # Create note
        note = RichNote(
            id=f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **note_data
        )
        
        # Launch editor
        edited_note = await self._launch_editor(note)
        return edited_note
    
    async def edit_note(self, note: RichNote) -> Optional[RichNote]:
        """Edit an existing note"""
        return await self._launch_editor(note)
    
    async def _get_note_metadata(self, topic: str = "") -> Optional[Dict[str, Any]]:
        """Get note metadata from user"""
        try:
            # Title
            title = input(self.formatter._colorize("Note Title: ", Color.BRIGHT_GREEN)).strip()
            if not title:
                return None
            
            # Type selection
            type_items = [
                MenuItem("1", "💡", "Concept", "Key concept or definition", color=Color.BRIGHT_BLUE),
                MenuItem("2", "📋", "Example", "Code example or use case", color=Color.BRIGHT_GREEN),
                MenuItem("3", "❓", "Question", "Question to research later", color=Color.BRIGHT_YELLOW),
                MenuItem("4", "🔍", "Insight", "Personal insight or discovery", color=Color.BRIGHT_MAGENTA),
                MenuItem("5", "✅", "Todo", "Action item or task", color=Color.BRIGHT_CYAN),
                MenuItem("6", "🔗", "Reference", "External reference or link", color=Color.WHITE)
            ]
            
            nav = NavigationController(self.formatter)
            _, type_key = await nav.show_menu("Select Note Type", type_items)
            
            if type_key == 'quit':
                return None
            
            type_mapping = {
                "1": NoteType.CONCEPT,
                "2": NoteType.EXAMPLE,
                "3": NoteType.QUESTION,
                "4": NoteType.INSIGHT,
                "5": NoteType.TODO,
                "6": NoteType.REFERENCE
            }
            note_type = type_mapping.get(type_key, NoteType.CONCEPT)
            
            # Priority selection
            priority_items = [
                MenuItem("1", "🔴", "Urgent", "Needs immediate attention", color=Color.BRIGHT_RED),
                MenuItem("2", "🟠", "Critical", "Very important", color=Color.BRIGHT_YELLOW),
                MenuItem("3", "🟡", "High", "Important", color=Color.BRIGHT_GREEN),
                MenuItem("4", "🟢", "Medium", "Normal priority", color=Color.BRIGHT_CYAN),
                MenuItem("5", "🔵", "Low", "Nice to have", color=Color.BRIGHT_BLACK)
            ]
            
            _, priority_key = await nav.show_menu("Select Priority", priority_items)
            
            if priority_key == 'quit':
                return None
            
            priority_mapping = {
                "1": Priority.URGENT,
                "2": Priority.CRITICAL, 
                "3": Priority.HIGH,
                "4": Priority.MEDIUM,
                "5": Priority.LOW
            }
            priority = priority_mapping.get(priority_key, Priority.MEDIUM)
            
            # Tags
            tags_input = input(self.formatter._colorize("Tags (comma-separated): ", Color.BRIGHT_BLUE)).strip()
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            
            return {
                'title': title,
                'content': '',
                'note_type': note_type,
                'priority': priority,
                'tags': tags,
                'topic': topic
            }
            
        except (EOFError, KeyboardInterrupt):
            return None
    
    async def _launch_editor(self, note: RichNote) -> Optional[RichNote]:
        """Launch the rich text editor"""
        self.current_note = note
        self.editing_mode = True
        
        print('\033[2J\033[H', end='')
        print(self.formatter.header(f"Editing: {note.title}", level=2))
        
        # Show current content if exists
        if note.content:
            print(self.formatter._colorize("Current content:", Color.BRIGHT_CYAN))
            print(self.formatter.box(note.formatted_content, style="single"))
        
        print(self.formatter._colorize("\nEnter your content (type /help for formatting commands):", 
                                     Color.BRIGHT_YELLOW))
        print(self.formatter._colorize("Press Ctrl+D or type /save when finished", Color.BRIGHT_GREEN))
        
        # Content input with live formatting
        content_lines = []
        
        while self.editing_mode:
            try:
                line = input(self.formatter._colorize(">>> ", Color.BRIGHT_MAGENTA))
                
                # Check for commands
                if line.startswith('/'):
                    command_result = await self._handle_command(line, content_lines)
                    if command_result == 'save':
                        break
                    elif command_result == 'cancel':
                        return None
                else:
                    content_lines.append(line)
                    # Show formatted preview
                    await self._show_preview(content_lines)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                confirm = input(self.formatter._colorize("\nDiscard changes? (y/N): ", Color.BRIGHT_RED))
                if confirm.lower() == 'y':
                    return None
        
        # Update note content
        note.content = '\n'.join(content_lines)
        note.formatted_content = note._format_content()
        note.timestamp = datetime.now().isoformat()
        
        return note
    
    async def _handle_command(self, command: str, content_lines: List[str]) -> Optional[str]:
        """Handle editor commands"""
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in self.commands:
            return await self.commands[cmd](args, content_lines)
        else:
            print(self.formatter.warning(f"Unknown command: {cmd}. Type /help for available commands."))
            return None
    
    async def _insert_bold(self, args: str, content_lines: List[str]) -> None:
        """Insert bold text"""
        if args:
            content_lines.append(f"**{args}**")
        else:
            print(self.formatter.info("Usage: /bold <text>"))
    
    async def _insert_italic(self, args: str, content_lines: List[str]) -> None:
        """Insert italic text"""
        if args:
            content_lines.append(f"*{args}*")
        else:
            print(self.formatter.info("Usage: /italic <text>"))
    
    async def _insert_code(self, args: str, content_lines: List[str]) -> None:
        """Insert code snippet"""
        if args:
            content_lines.append(f"`{args}`")
        else:
            print(self.formatter.info("Usage: /code <code>"))
    
    async def _insert_header(self, args: str, content_lines: List[str]) -> None:
        """Insert header"""
        if args:
            content_lines.append(f"# {args}")
        else:
            print(self.formatter.info("Usage: /header <title>"))
    
    async def _insert_list(self, args: str, content_lines: List[str]) -> None:
        """Insert list item"""
        if args:
            content_lines.append(f"- {args}")
        else:
            print(self.formatter.info("Usage: /list <item>"))
    
    async def _insert_link(self, args: str, content_lines: List[str]) -> None:
        """Insert link"""
        if args:
            content_lines.append(f"[Link: {args}]")
        else:
            print(self.formatter.info("Usage: /link <url>"))
    
    async def _save_note(self, args: str, content_lines: List[str]) -> str:
        """Save the note"""
        self.editing_mode = False
        return 'save'
    
    async def _cancel_edit(self, args: str, content_lines: List[str]) -> str:
        """Cancel editing"""
        self.editing_mode = False
        return 'cancel'
    
    async def _show_help(self, args: str, content_lines: List[str]) -> None:
        """Show editor help"""
        help_content = """
        FORMATTING COMMANDS:
        /bold <text>     - Make text bold (**text**)
        /italic <text>   - Make text italic (*text*)
        /code <code>     - Insert code snippet (`code`)
        /header <title>  - Insert header (# Header)
        /list <item>     - Insert list item (- item)
        /link <url>      - Insert link reference
        
        EDITOR COMMANDS:
        /save           - Save note and exit
        /cancel         - Cancel editing
        /help           - Show this help
        
        DIRECT FORMATTING:
        **text**        - Bold text
        *text*          - Italic text
        `code`          - Inline code
        # Header        - Header text
        - item          - List item
        1. item         - Numbered list
        """
        
        print(self.formatter.box(help_content, title="Editor Help", 
                               style="double", color=Color.BRIGHT_BLUE))
    
    async def _show_preview(self, content_lines: List[str]) -> None:
        """Show formatted preview of content"""
        if len(content_lines) > 0:
            # Create temporary note for preview
            temp_note = RichNote(
                id="preview",
                title="Preview",
                content='\n'.join(content_lines[-3:]),  # Show last 3 lines
                note_type=NoteType.CONCEPT,
                priority=Priority.MEDIUM
            )
            
            print(self.formatter._colorize("Preview:", Color.BRIGHT_BLACK))
            print(temp_note.formatted_content)


class NotesManager:
    """Manage note collections with advanced features"""
    
    def __init__(self, formatter: TerminalFormatter, notes_dir: str = "notes"):
        self.formatter = formatter
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(exist_ok=True)
        self.notes: Dict[str, RichNote] = {}
        self.tags_index: Dict[str, List[str]] = {}  # tag -> note_ids
        self.topics_index: Dict[str, List[str]] = {}  # topic -> note_ids
        
        self.editor = NoteEditor(formatter)
        self.load_notes()
    
    def load_notes(self) -> None:
        """Load all notes from disk"""
        notes_file = self.notes_dir / "notes.json"
        
        if notes_file.exists():
            try:
                with open(notes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for note_data in data.get('notes', []):
                    # Convert enum strings back to enums
                    note_data['note_type'] = NoteType(note_data['note_type'])
                    note_data['priority'] = Priority(note_data['priority'])
                    
                    note = RichNote(**note_data)
                    self.notes[note.id] = note
                    
                    # Update indices
                    self._update_indices(note)
                    
            except Exception as e:
                self.formatter.error(f"Error loading notes: {e}")
    
    def save_notes(self) -> None:
        """Save all notes to disk"""
        notes_file = self.notes_dir / "notes.json"
        
        try:
            # Convert notes to serializable format
            notes_data = []
            for note in self.notes.values():
                note_dict = asdict(note)
                # Convert enums to strings
                note_dict['note_type'] = note.note_type.value
                note_dict['priority'] = note.priority.value
                notes_data.append(note_dict)
            
            data = {
                'notes': notes_data,
                'created': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.formatter.success(f"Notes saved to {notes_file}")
            
        except Exception as e:
            self.formatter.error(f"Error saving notes: {e}")
    
    async def create_note(self, topic: str = "") -> Optional[RichNote]:
        """Create a new note"""
        note = await self.editor.create_new_note(topic)
        
        if note:
            self.notes[note.id] = note
            self._update_indices(note)
            self.save_notes()
            
            # Show success message
            print(self.formatter.success(f"Note '{note.title}' created successfully!"))
            
        return note
    
    async def edit_note(self, note_id: str) -> Optional[RichNote]:
        """Edit an existing note"""
        if note_id not in self.notes:
            self.formatter.error("Note not found")
            return None
        
        note = await self.editor.edit_note(self.notes[note_id])
        
        if note:
            self.notes[note_id] = note
            self._update_indices(note)
            self.save_notes()
            
        return note
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        if note_id not in self.notes:
            return False
        
        note = self.notes[note_id]
        
        # Remove from indices
        for tag in note.tags:
            if tag in self.tags_index:
                self.tags_index[tag].remove(note_id)
                if not self.tags_index[tag]:
                    del self.tags_index[tag]
        
        if note.topic in self.topics_index:
            self.topics_index[note.topic].remove(note_id)
            if not self.topics_index[note.topic]:
                del self.topics_index[note.topic]
        
        # Remove note
        del self.notes[note_id]
        self.save_notes()
        
        return True
    
    def search_notes(self, query: str, search_type: str = "all") -> List[RichNote]:
        """Search notes by various criteria"""
        results = []
        query_lower = query.lower()
        
        for note in self.notes.values():
            if search_type == "title" and query_lower in note.title.lower():
                results.append(note)
            elif search_type == "content" and query_lower in note.content.lower():
                results.append(note)
            elif search_type == "tags" and any(query_lower in tag.lower() for tag in note.tags):
                results.append(note)
            elif search_type == "all":
                if (query_lower in note.title.lower() or 
                    query_lower in note.content.lower() or
                    query_lower in note.topic.lower() or
                    any(query_lower in tag.lower() for tag in note.tags)):
                    results.append(note)
        
        # Sort by priority and recency
        results.sort(key=lambda n: (n.priority.value, n.timestamp), reverse=True)
        return results
    
    def get_notes_by_topic(self, topic: str) -> List[RichNote]:
        """Get all notes for a specific topic"""
        if topic in self.topics_index:
            return [self.notes[note_id] for note_id in self.topics_index[topic]]
        return []
    
    def get_notes_by_tag(self, tag: str) -> List[RichNote]:
        """Get all notes with a specific tag"""
        if tag in self.tags_index:
            return [self.notes[note_id] for note_id in self.tags_index[tag]]
        return []
    
    async def display_note(self, note: RichNote) -> None:
        """Display a note with rich formatting"""
        # Clear screen
        print('\033[2J\033[H', end='')
        
        # Note header
        priority_icons = {
            Priority.URGENT: "🔴",
            Priority.CRITICAL: "🟠", 
            Priority.HIGH: "🟡",
            Priority.MEDIUM: "🟢",
            Priority.LOW: "🔵"
        }
        
        type_icons = {
            NoteType.CONCEPT: "💡",
            NoteType.EXAMPLE: "📋",
            NoteType.QUESTION: "❓",
            NoteType.INSIGHT: "🔍",
            NoteType.TODO: "✅",
            NoteType.REFERENCE: "🔗"
        }
        
        priority_icon = priority_icons.get(note.priority, "⚪")
        type_icon = type_icons.get(note.note_type, "📝")
        
        header = f"{priority_icon} {type_icon} {note.title}"
        print(self.formatter.header(header, level=1, style="boxed"))
        
        # Metadata
        timestamp = datetime.fromisoformat(note.timestamp).strftime("%Y-%m-%d %H:%M")
        metadata = f"Created: {timestamp} | Type: {note.note_type.value.title()} | Priority: {note.priority.name}"
        
        if note.topic:
            metadata += f" | Topic: {note.topic}"
        
        print(self.formatter._colorize(metadata, Color.BRIGHT_BLACK))
        
        # Tags
        if note.tags:
            tags_text = " ".join(f"#{tag}" for tag in note.tags)
            print(self.formatter._colorize(f"Tags: {tags_text}", Color.BRIGHT_BLUE))
        
        print()
        
        # Content with rich formatting
        if note.formatted_content:
            print(note.formatted_content)
        else:
            print(note.content)
        
        # Code snippets
        if note.code_snippets:
            print(self.formatter.header("Code Snippets", level=3))
            for i, snippet in enumerate(note.code_snippets, 1):
                lang = snippet.get('language', 'text')
                code = snippet.get('code', '')
                print(self.formatter.box(code, title=f"Snippet {i} ({lang})", 
                                       style="single", color=Color.BRIGHT_GREEN))
        
        # Links
        if note.links:
            print(self.formatter.header("References", level=3))
            for link in note.links:
                print(f"  🔗 {link}")
    
    def _update_indices(self, note: RichNote) -> None:
        """Update search indices"""
        # Tags index
        for tag in note.tags:
            if tag not in self.tags_index:
                self.tags_index[tag] = []
            if note.id not in self.tags_index[tag]:
                self.tags_index[tag].append(note.id)
        
        # Topics index
        if note.topic:
            if note.topic not in self.topics_index:
                self.topics_index[note.topic] = []
            if note.id not in self.topics_index[note.topic]:
                self.topics_index[note.topic].append(note.id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get note collection statistics"""
        total_notes = len(self.notes)
        notes_by_type = {}
        notes_by_priority = {}
        
        for note in self.notes.values():
            # Count by type
            note_type = note.note_type.value
            notes_by_type[note_type] = notes_by_type.get(note_type, 0) + 1
            
            # Count by priority
            priority = note.priority.name
            notes_by_priority[priority] = notes_by_priority.get(priority, 0) + 1
        
        return {
            'total_notes': total_notes,
            'notes_by_type': notes_by_type,
            'notes_by_priority': notes_by_priority,
            'total_tags': len(self.tags_index),
            'total_topics': len(self.topics_index),
            'most_used_tags': sorted(self.tags_index.items(), 
                                   key=lambda x: len(x[1]), reverse=True)[:5]
        }