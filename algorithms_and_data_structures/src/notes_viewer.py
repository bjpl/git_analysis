#!/usr/bin/env python3
"""
Enhanced Notes Viewer - Interactive note browsing with pagination and filtering
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import math
import re
from difflib import SequenceMatcher

class EnhancedNotesViewer:
    """Advanced notes viewing with pagination, sorting, and filtering"""
    
    def __init__(self, db_path: str = "curriculum.db"):
        self.db_path = db_path
        self.page_size = 5  # Notes per page
        self._current_page = 1  # Ensure it's an integer
        self._total_pages = 1  # Ensure it's an integer
        self.sort_by = "created_desc"  # Default sort
        self.filter_module = None
        self.filter_tags = []
        self.search_query = ""
        self.notes_cache = []
        self.total_notes = 0
    
    @property
    def current_page(self):
        """Ensure current_page is always an integer"""
        return int(self._current_page) if self._current_page is not None else 1
    
    @current_page.setter
    def current_page(self, value):
        """Set current_page, ensuring it's an integer"""
        self._current_page = int(value) if value is not None else 1
    
    @property
    def total_pages(self):
        """Ensure total_pages is always an integer"""
        return int(self._total_pages) if self._total_pages is not None else 1
    
    @total_pages.setter
    def total_pages(self, value):
        """Set total_pages, ensuring it's an integer"""
        self._total_pages = int(value) if value is not None else 1
        
    def get_filtered_notes(self, user_id: int = 1) -> List[Dict]:
        """Get notes with current filters applied"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query
            query = """
                SELECT n.id, n.lesson_id, n.module_name, n.topic, 
                       n.content, n.tags, n.created_at, n.updated_at, 
                       n.is_favorite, l.title as lesson_title
                FROM notes n
                LEFT JOIN lessons l ON n.lesson_id = l.id
                WHERE n.user_id = ?
            """
            params = [user_id]
            
            # Apply module filter
            if self.filter_module:
                query += " AND n.module_name = ?"
                params.append(self.filter_module)
            
            # Apply search query
            if self.search_query:
                query += " AND (n.content LIKE ? OR n.topic LIKE ? OR n.tags LIKE ?)"
                search_pattern = f"%{self.search_query}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            # Apply sorting
            sort_options = {
                "created_desc": "n.created_at DESC",
                "created_asc": "n.created_at ASC",
                "updated_desc": "n.updated_at DESC",
                "title_asc": "n.topic ASC",
                "title_desc": "n.topic DESC",
                "module_asc": "n.module_name ASC, n.created_at DESC",
                "favorites": "n.is_favorite DESC, n.created_at DESC"
            }
            query += f" ORDER BY {sort_options.get(self.sort_by, 'n.created_at DESC')}"
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            notes = []
            
            for row in cursor.fetchall():
                note = dict(zip(columns, row))
                note['tags'] = json.loads(note['tags']) if note['tags'] else []
                
                # Apply tag filter
                if self.filter_tags:
                    if not any(tag in note['tags'] for tag in self.filter_tags):
                        continue
                
                notes.append(note)
            
            return notes
    
    def fuzzy_search(self, notes: List[Dict], query: str, threshold: float = 0.6) -> List[Dict]:
        """Perform fuzzy search on notes"""
        if not query:
            return notes
        
        query_lower = query.lower()
        scored_notes = []
        
        for note in notes:
            # Calculate similarity scores for different fields
            topic_score = SequenceMatcher(None, query_lower, 
                                         note.get('topic', '').lower()).ratio()
            content_score = SequenceMatcher(None, query_lower, 
                                           note.get('content', '')[:200].lower()).ratio()
            module_score = SequenceMatcher(None, query_lower, 
                                          note.get('module_name', '').lower()).ratio()
            
            # Check tags
            tag_score = 0
            for tag in note.get('tags', []):
                tag_score = max(tag_score, 
                               SequenceMatcher(None, query_lower, tag.lower()).ratio())
            
            # Calculate weighted final score
            final_score = max(
                topic_score * 1.5,  # Title/topic has higher weight
                content_score * 1.0,
                module_score * 0.8,
                tag_score * 1.2
            )
            
            if final_score >= threshold:
                note['relevance_score'] = final_score
                scored_notes.append(note)
        
        # Sort by relevance score
        scored_notes.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_notes
    
    def get_page(self, page_num: int = None) -> List[Dict]:
        """Get a specific page of notes"""
        if page_num:
            self.current_page = page_num
        
        # Get all filtered notes
        all_notes = self.get_filtered_notes()
        
        # Apply fuzzy search if enabled
        if self.search_query and len(self.search_query) > 2:
            all_notes = self.fuzzy_search(all_notes, self.search_query)
        
        # Store for reference
        self.notes_cache = all_notes
        self.total_notes = len(all_notes)
        self.total_pages = max(1, math.ceil(self.total_notes / self.page_size))
        
        # Ensure current page is valid
        self.current_page = max(1, min(self.current_page, self.total_pages))
        
        # Calculate slice indices
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        
        return all_notes[start_idx:end_idx]
    
    def get_available_modules(self, user_id: int = 1) -> List[str]:
        """Get list of all modules that have notes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT module_name 
                FROM notes 
                WHERE user_id = ? AND module_name IS NOT NULL
                ORDER BY module_name
            """, (user_id,))
            return [row[0] for row in cursor.fetchall()]
    
    def get_all_tags(self, user_id: int = 1) -> List[Tuple[str, int]]:
        """Get all unique tags with their counts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tags FROM notes 
                WHERE user_id = ? AND tags IS NOT NULL
            """, (user_id,))
            
            tag_counts = {}
            for row in cursor.fetchall():
                tags = json.loads(row[0]) if row[0] else []
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Sort by count descending
            return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    def get_note_detail(self, note_id: int) -> Optional[Dict]:
        """Get full details of a specific note"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.*, l.title as lesson_title, l.description as lesson_desc
                FROM notes n
                LEFT JOIN lessons l ON n.lesson_id = l.id
                WHERE n.id = ?
            """, (note_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                note = dict(zip(columns, row))
                note['tags'] = json.loads(note['tags']) if note['tags'] else []
                return note
        return None
    
    def update_note(self, note_id: int, content: str = None, 
                    topic: str = None, tags: List[str] = None) -> bool:
        """Update a note with new content"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if content is not None:
                updates.append("content = ?")
                params.append(content)
            
            if topic is not None:
                updates.append("topic = ?")
                params.append(topic)
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(note_id)
            
            query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def toggle_favorite(self, note_id: int) -> bool:
        """Toggle the favorite status of a note"""
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
    
    def get_statistics(self, user_id: int = 1) -> Dict:
        """Get comprehensive statistics about notes"""
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
                LIMIT 5
            """, (user_id,))
            top_modules = cursor.fetchall()
            
            # Recent activity (last 30 days)
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM notes 
                WHERE user_id = ? 
                AND datetime(created_at) > datetime('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (user_id,))
            recent_activity = cursor.fetchall()
            
            # Favorite notes count
            cursor.execute("""
                SELECT COUNT(*) 
                FROM notes 
                WHERE user_id = ? AND is_favorite = 1
            """, (user_id,))
            favorites = cursor.fetchone()[0]
            
            # Average note length
            cursor.execute("""
                SELECT AVG(LENGTH(content))
                FROM notes 
                WHERE user_id = ?
            """, (user_id,))
            avg_length = cursor.fetchone()[0] or 0
            
            # Most used tags
            cursor.execute("""
                SELECT tags FROM notes 
                WHERE user_id = ? AND tags IS NOT NULL
            """, (user_id,))
            
            tag_counts = {}
            for row in cursor.fetchall():
                tags = json.loads(row[0]) if row[0] else []
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_notes': total_notes,
                'top_modules': top_modules,
                'recent_activity': recent_activity,
                'favorites': favorites,
                'avg_length': int(avg_length),
                'top_tags': top_tags,
                'notes_this_week': sum(count for _, count in recent_activity[:7]),
                'modules_count': len(self.get_available_modules(user_id))
            }
    
    def format_note_preview(self, note: Dict, max_length: int = 80) -> str:
        """Format a note for preview display"""
        content = note.get('content', '')
        
        # Remove markdown formatting for cleaner preview
        content = re.sub(r'[#*`_\[\]()]', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
    
    def export_filtered_notes(self, format: str = "markdown") -> str:
        """Export currently filtered notes"""
        notes = self.notes_cache if self.notes_cache else self.get_filtered_notes()
        
        if format == "markdown":
            lines = [f"# 📚 Filtered Notes Export\n"]
            lines.append(f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
            lines.append(f"*Total Notes: {len(notes)}*\n\n")
            
            if self.filter_module:
                lines.append(f"**Module Filter:** {self.filter_module}\n")
            if self.filter_tags:
                lines.append(f"**Tag Filter:** {', '.join(self.filter_tags)}\n")
            if self.search_query:
                lines.append(f"**Search Query:** {self.search_query}\n")
            lines.append("\n---\n\n")
            
            for note in notes:
                lines.append(f"## {note.get('topic', 'Untitled')}\n")
                lines.append(f"*{note.get('module_name', 'General')} | ")
                lines.append(f"{note.get('created_at', '')}*\n\n")
                
                if note.get('tags'):
                    lines.append(f"**Tags:** {', '.join(note['tags'])}\n\n")
                
                lines.append(f"{note.get('content', '')}\n\n")
                lines.append("---\n\n")
            
            return '\n'.join(lines)
        
        elif format == "json":
            # Clean notes for JSON export
            export_notes = []
            for note in notes:
                clean_note = {k: v for k, v in note.items() 
                             if k not in ['relevance_score']}
                export_notes.append(clean_note)
            
            return json.dumps(export_notes, indent=2, default=str)
        
        return ""


def test_viewer():
    """Test the enhanced viewer functionality"""
    viewer = EnhancedNotesViewer()
    
    # Test getting modules
    modules = viewer.get_available_modules()
    print(f"Available modules: {modules}")
    
    # Test getting tags
    tags = viewer.get_all_tags()
    print(f"Top tags: {tags[:5]}")
    
    # Test pagination
    viewer.page_size = 3
    page1 = viewer.get_page(1)
    print(f"Page 1 ({len(page1)} notes): {viewer.current_page}/{viewer.total_pages}")
    
    # Test filtering
    viewer.filter_module = modules[0] if modules else None
    filtered = viewer.get_page(1)
    print(f"Filtered by module: {len(filtered)} notes")
    
    # Test statistics
    stats = viewer.get_statistics()
    print(f"Statistics: {stats['total_notes']} total notes")


if __name__ == "__main__":
    test_viewer()