"""Collection management system for favorites, vocabulary sets, and sharing."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import zipfile
import csv
from io import StringIO


class CollectionType(Enum):
    """Types of collections."""
    FAVORITES = "favorites"
    VOCABULARY = "vocabulary"
    CUSTOM = "custom"
    LEARNING_SET = "learning_set"
    BATCH_RESULTS = "batch_results"


class SortOrder(Enum):
    """Sort order options."""
    DATE_ADDED_DESC = "date_added_desc"
    DATE_ADDED_ASC = "date_added_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    USAGE_COUNT_DESC = "usage_count_desc"
    CUSTOM_ORDER = "custom_order"


@dataclass
class CollectionItem:
    """Individual item in a collection."""
    id: str
    item_type: str  # 'image', 'vocabulary', 'phrase'
    content: Dict[str, Any]
    date_added: str
    custom_order: int = 0
    tags: List[str] = None
    notes: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Collection:
    """Collection of items (images, vocabulary, etc.)."""
    id: str
    name: str
    description: str
    collection_type: CollectionType
    created_at: str
    updated_at: str
    items: List[CollectionItem] = None
    tags: List[str] = None
    settings: Dict[str, Any] = None
    is_shared: bool = False
    share_code: Optional[str] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.tags is None:
            self.tags = []
        if self.settings is None:
            self.settings = {}


class CollectionManager:
    """Manages collections of images, vocabulary, and learning sets."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "collections.db"
        self.exports_dir = data_dir / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the collections database."""
        with sqlite3.connect(self.db_path) as conn:
            # Collections table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collections (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    collection_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT,
                    settings TEXT,
                    is_shared BOOLEAN DEFAULT FALSE,
                    share_code TEXT UNIQUE
                )
            """)
            
            # Collection items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_items (
                    id TEXT PRIMARY KEY,
                    collection_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    date_added TEXT NOT NULL,
                    custom_order INTEGER DEFAULT 0,
                    tags TEXT,
                    notes TEXT,
                    metadata TEXT,
                    FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE
                )
            """)
            
            # Collection sharing table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_shares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_id TEXT NOT NULL,
                    shared_with TEXT,
                    permission_level TEXT DEFAULT 'view',
                    shared_at TEXT NOT NULL,
                    expires_at TEXT,
                    FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE
                )
            """)
            
            # Collection statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_stats (
                    collection_id TEXT PRIMARY KEY,
                    view_count INTEGER DEFAULT 0,
                    last_viewed TEXT,
                    item_count INTEGER DEFAULT 0,
                    total_size_bytes INTEGER DEFAULT 0,
                    FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
    
    def create_collection(self, name: str, description: str = "", 
                         collection_type: CollectionType = CollectionType.CUSTOM,
                         tags: List[str] = None) -> str:
        """Create a new collection."""
        collection_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO collections 
                    (id, name, description, collection_type, created_at, updated_at, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    collection_id,
                    name,
                    description,
                    collection_type.value,
                    now,
                    now,
                    json.dumps(tags or [])
                ))
                
                # Initialize stats
                conn.execute("""
                    INSERT INTO collection_stats (collection_id, item_count)
                    VALUES (?, 0)
                """, (collection_id,))
                
                return collection_id
            except sqlite3.IntegrityError:
                raise ValueError(f"Collection with name '{name}' already exists")
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get a collection by ID."""
        with sqlite3.connect(self.db_path) as conn:
            # Get collection info
            row = conn.execute("""
                SELECT id, name, description, collection_type, created_at, 
                       updated_at, tags, settings, is_shared, share_code
                FROM collections WHERE id = ?
            """, (collection_id,)).fetchone()
            
            if not row:
                return None
            
            # Get collection items
            item_rows = conn.execute("""
                SELECT id, item_type, content, date_added, custom_order, 
                       tags, notes, metadata
                FROM collection_items 
                WHERE collection_id = ?
                ORDER BY custom_order ASC, date_added ASC
            """, (collection_id,)).fetchall()
            
            items = []
            for item_row in item_rows:
                items.append(CollectionItem(
                    id=item_row[0],
                    item_type=item_row[1],
                    content=json.loads(item_row[2]),
                    date_added=item_row[3],
                    custom_order=item_row[4],
                    tags=json.loads(item_row[5]) if item_row[5] else [],
                    notes=item_row[6] or "",
                    metadata=json.loads(item_row[7]) if item_row[7] else {}
                ))
            
            return Collection(
                id=row[0],
                name=row[1],
                description=row[2] or "",
                collection_type=CollectionType(row[3]),
                created_at=row[4],
                updated_at=row[5],
                items=items,
                tags=json.loads(row[6]) if row[6] else [],
                settings=json.loads(row[7]) if row[7] else {},
                is_shared=bool(row[8]),
                share_code=row[9]
            )
    
    def list_collections(self, collection_type: Optional[CollectionType] = None) -> List[Collection]:
        """List all collections, optionally filtered by type."""
        with sqlite3.connect(self.db_path) as conn:
            if collection_type:
                rows = conn.execute("""
                    SELECT c.id, c.name, c.description, c.collection_type, 
                           c.created_at, c.updated_at, c.tags, c.settings,
                           c.is_shared, c.share_code, s.item_count
                    FROM collections c
                    LEFT JOIN collection_stats s ON c.id = s.collection_id
                    WHERE c.collection_type = ?
                    ORDER BY c.updated_at DESC
                """, (collection_type.value,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT c.id, c.name, c.description, c.collection_type, 
                           c.created_at, c.updated_at, c.tags, c.settings,
                           c.is_shared, c.share_code, s.item_count
                    FROM collections c
                    LEFT JOIN collection_stats s ON c.id = s.collection_id
                    ORDER BY c.updated_at DESC
                """).fetchall()
            
            collections = []
            for row in rows:
                # Get basic collection info without loading all items
                collection = Collection(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    collection_type=CollectionType(row[3]),
                    created_at=row[4],
                    updated_at=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                    settings=json.loads(row[7]) if row[7] else {},
                    is_shared=bool(row[8]),
                    share_code=row[9]
                )
                # Add item count to metadata
                collection.settings['item_count'] = row[10] or 0
                collections.append(collection)
            
            return collections
    
    def add_item_to_collection(self, collection_id: str, item_type: str, 
                              content: Dict[str, Any], tags: List[str] = None,
                              notes: str = "", custom_order: int = 0) -> str:
        """Add an item to a collection."""
        item_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Add item
            conn.execute("""
                INSERT INTO collection_items 
                (id, collection_id, item_type, content, date_added, 
                 custom_order, tags, notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                collection_id,
                item_type,
                json.dumps(content),
                now,
                custom_order,
                json.dumps(tags or []),
                notes,
                json.dumps({})
            ))
            
            # Update collection timestamp and stats
            conn.execute("""
                UPDATE collections SET updated_at = ? WHERE id = ?
            """, (now, collection_id))
            
            conn.execute("""
                UPDATE collection_stats 
                SET item_count = item_count + 1
                WHERE collection_id = ?
            """, (collection_id,))
            
            return item_id
    
    def remove_item_from_collection(self, collection_id: str, item_id: str) -> bool:
        """Remove an item from a collection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM collection_items 
                WHERE id = ? AND collection_id = ?
            """, (item_id, collection_id))
            
            if cursor.rowcount > 0:
                # Update collection timestamp and stats
                now = datetime.now().isoformat()
                conn.execute("""
                    UPDATE collections SET updated_at = ? WHERE id = ?
                """, (now, collection_id))
                
                conn.execute("""
                    UPDATE collection_stats 
                    SET item_count = item_count - 1
                    WHERE collection_id = ?
                """, (collection_id,))
                
                return True
            
            return False
    
    def add_image_to_favorites(self, image_data: Dict[str, Any], 
                              notes: str = "") -> str:
        """Add an image to the favorites collection."""
        # Get or create favorites collection
        favorites_id = self._get_or_create_favorites_collection()
        
        # Check if image already exists in favorites
        image_url = image_data.get('url', '')
        if self._item_exists_in_collection(favorites_id, 'image', image_url):
            raise ValueError("Image already in favorites")
        
        return self.add_item_to_collection(
            favorites_id, 'image', image_data, 
            tags=['favorite'], notes=notes
        )
    
    def add_vocabulary_to_collection(self, collection_id: str, 
                                   spanish_word: str, english_translation: str,
                                   context: str = "", tags: List[str] = None) -> str:
        """Add vocabulary to a collection."""
        vocabulary_data = {
            'spanish': spanish_word,
            'english': english_translation,
            'context': context,
            'date_learned': datetime.now().isoformat(),
            'difficulty': 1,  # 1-5 scale
            'review_count': 0,
            'success_rate': 0.0
        }
        
        return self.add_item_to_collection(
            collection_id, 'vocabulary', vocabulary_data, tags or []
        )
    
    def create_vocabulary_set(self, name: str, words: List[Dict[str, str]],
                             description: str = "", tags: List[str] = None) -> str:
        """Create a new vocabulary learning set."""
        collection_id = self.create_collection(
            name, description, CollectionType.VOCABULARY, tags
        )
        
        for word_data in words:
            self.add_vocabulary_to_collection(
                collection_id,
                word_data.get('spanish', ''),
                word_data.get('english', ''),
                word_data.get('context', ''),
                word_data.get('tags', [])
            )
        
        return collection_id
    
    def update_collection(self, collection_id: str, name: Optional[str] = None,
                         description: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> bool:
        """Update collection metadata."""
        with sqlite3.connect(self.db_path) as conn:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(collection_id)
                
                cursor = conn.execute(f"""
                    UPDATE collections 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
                
                return cursor.rowcount > 0
            
            return False
    
    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection and all its items."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM collections WHERE id = ?", 
                (collection_id,)
            )
            return cursor.rowcount > 0
    
    def search_collections(self, query: str, 
                          collection_type: Optional[CollectionType] = None) -> List[Collection]:
        """Search collections by name, description, or tags."""
        with sqlite3.connect(self.db_path) as conn:
            sql = """
                SELECT id, name, description, collection_type, created_at, 
                       updated_at, tags, settings, is_shared, share_code
                FROM collections 
                WHERE (name LIKE ? OR description LIKE ? OR tags LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            
            if collection_type:
                sql += " AND collection_type = ?"
                params.append(collection_type.value)
            
            sql += " ORDER BY updated_at DESC"
            
            rows = conn.execute(sql, params).fetchall()
            
            collections = []
            for row in rows:
                collections.append(Collection(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    collection_type=CollectionType(row[3]),
                    created_at=row[4],
                    updated_at=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                    settings=json.loads(row[7]) if row[7] else {},
                    is_shared=bool(row[8]),
                    share_code=row[9]
                ))
            
            return collections
    
    def sort_collection(self, collection_id: str, sort_order: SortOrder) -> bool:
        """Sort items in a collection."""
        collection = self.get_collection(collection_id)
        if not collection:
            return False
        
        items = collection.items
        
        if sort_order == SortOrder.DATE_ADDED_ASC:
            items.sort(key=lambda x: x.date_added)
        elif sort_order == SortOrder.DATE_ADDED_DESC:
            items.sort(key=lambda x: x.date_added, reverse=True)
        elif sort_order == SortOrder.NAME_ASC:
            items.sort(key=lambda x: x.content.get('name', x.content.get('spanish', '')))
        elif sort_order == SortOrder.NAME_DESC:
            items.sort(key=lambda x: x.content.get('name', x.content.get('spanish', '')), reverse=True)
        elif sort_order == SortOrder.USAGE_COUNT_DESC:
            items.sort(key=lambda x: x.metadata.get('usage_count', 0), reverse=True)
        elif sort_order == SortOrder.CUSTOM_ORDER:
            items.sort(key=lambda x: x.custom_order)
        
        # Update custom_order values in database
        with sqlite3.connect(self.db_path) as conn:
            for i, item in enumerate(items):
                conn.execute("""
                    UPDATE collection_items 
                    SET custom_order = ?
                    WHERE id = ?
                """, (i, item.id))
        
        return True
    
    def share_collection(self, collection_id: str, 
                        permission_level: str = 'view',
                        expires_days: Optional[int] = None) -> str:
        """Share a collection and return share code."""
        share_code = str(uuid.uuid4())[:8].upper()
        now = datetime.now().isoformat()
        expires_at = None
        
        if expires_days:
            from datetime import timedelta
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Update collection with share code
            conn.execute("""
                UPDATE collections 
                SET is_shared = TRUE, share_code = ?
                WHERE id = ?
            """, (share_code, collection_id))
            
            # Add sharing record
            conn.execute("""
                INSERT INTO collection_shares 
                (collection_id, permission_level, shared_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (collection_id, permission_level, now, expires_at))
        
        return share_code
    
    def get_shared_collection(self, share_code: str) -> Optional[Collection]:
        """Get a collection by share code."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT c.id FROM collections c
                JOIN collection_shares s ON c.id = s.collection_id
                WHERE c.share_code = ? 
                AND (s.expires_at IS NULL OR s.expires_at > ?)
            """, (share_code, datetime.now().isoformat())).fetchone()
            
            if row:
                return self.get_collection(row[0])
            
            return None
    
    def export_collection(self, collection_id: str, 
                         format_type: str = 'json') -> str:
        """Export collection in specified format."""
        collection = self.get_collection(collection_id)
        if not collection:
            raise ValueError("Collection not found")
        
        if format_type == 'json':
            export_data = {
                'collection': asdict(collection),
                'export_timestamp': datetime.now().isoformat(),
                'format_version': '1.0'
            }
            return json.dumps(export_data, indent=2)
        
        elif format_type == 'csv' and collection.collection_type == CollectionType.VOCABULARY:
            output = StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow(['Spanish', 'English', 'Context', 'Date Added', 'Tags', 'Notes'])
            
            for item in collection.items:
                if item.item_type == 'vocabulary':
                    writer.writerow([
                        item.content.get('spanish', ''),
                        item.content.get('english', ''),
                        item.content.get('context', ''),
                        item.date_added,
                        ', '.join(item.tags),
                        item.notes
                    ])
            
            return output.getvalue()
        
        elif format_type == 'anki' and collection.collection_type == CollectionType.VOCABULARY:
            output = StringIO()
            
            for item in collection.items:
                if item.item_type == 'vocabulary':
                    spanish = item.content.get('spanish', '')
                    english = item.content.get('english', '')
                    context = item.content.get('context', '')[:50]
                    notes = item.notes[:50] if item.notes else ''
                    
                    # Anki format: front[tab]back[tab]tags
                    front = spanish
                    back = f"{english}\n{context}\n{notes}"
                    tags = ' '.join(item.tags)
                    
                    output.write(f"{front}\t{back}\t{tags}\n")
            
            return output.getvalue()
        
        return json.dumps(asdict(collection), indent=2)
    
    def export_collection_to_file(self, collection_id: str, 
                                 format_type: str = 'json') -> Path:
        """Export collection to file and return file path."""
        collection = self.get_collection(collection_id)
        if not collection:
            raise ValueError("Collection not found")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = collection.name.replace(' ', '_').replace('/', '_')
        filename = f"{safe_name}_{timestamp}.{format_type}"
        
        export_path = self.exports_dir / filename
        
        # Export data
        export_data = self.export_collection(collection_id, format_type)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(export_data)
        
        return export_path
    
    def import_collection(self, data: str, format_type: str = 'json') -> str:
        """Import collection from data string."""
        if format_type == 'json':
            import_data = json.loads(data)
            collection_data = import_data.get('collection', import_data)
            
            # Create new collection
            original_name = collection_data.get('name', 'Imported Collection')
            name = f"{original_name} (Imported)"
            
            collection_id = self.create_collection(
                name=name,
                description=collection_data.get('description', ''),
                collection_type=CollectionType(collection_data.get('collection_type', 'custom')),
                tags=collection_data.get('tags', [])
            )
            
            # Import items
            for item_data in collection_data.get('items', []):
                self.add_item_to_collection(
                    collection_id,
                    item_data.get('item_type', 'custom'),
                    item_data.get('content', {}),
                    item_data.get('tags', []),
                    item_data.get('notes', ''),
                    item_data.get('custom_order', 0)
                )
            
            return collection_id
        
        raise ValueError(f"Unsupported import format: {format_type}")
    
    def get_collection_statistics(self, collection_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a collection."""
        with sqlite3.connect(self.db_path) as conn:
            # Basic stats
            stats_row = conn.execute("""
                SELECT view_count, last_viewed, item_count, total_size_bytes
                FROM collection_stats WHERE collection_id = ?
            """, (collection_id,)).fetchone()
            
            if not stats_row:
                return {}
            
            # Item type breakdown
            type_breakdown = conn.execute("""
                SELECT item_type, COUNT(*) as count
                FROM collection_items 
                WHERE collection_id = ?
                GROUP BY item_type
            """, (collection_id,)).fetchall()
            
            # Recent activity
            recent_items = conn.execute("""
                SELECT item_type, date_added
                FROM collection_items 
                WHERE collection_id = ?
                ORDER BY date_added DESC
                LIMIT 10
            """, (collection_id,)).fetchall()
            
            return {
                'view_count': stats_row[0] or 0,
                'last_viewed': stats_row[1],
                'item_count': stats_row[2] or 0,
                'total_size_bytes': stats_row[3] or 0,
                'type_breakdown': {row[0]: row[1] for row in type_breakdown},
                'recent_items': [{
                    'type': row[0], 
                    'date_added': row[1]
                } for row in recent_items]
            }
    
    def _get_or_create_favorites_collection(self) -> str:
        """Get or create the favorites collection."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT id FROM collections 
                WHERE collection_type = ? AND name = ?
            """, (CollectionType.FAVORITES.value, "Favorites")).fetchone()
            
            if row:
                return row[0]
            else:
                return self.create_collection(
                    "Favorites", 
                    "Your favorite images", 
                    CollectionType.FAVORITES
                )
    
    def _item_exists_in_collection(self, collection_id: str, 
                                  item_type: str, identifier: str) -> bool:
        """Check if an item already exists in a collection."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT 1 FROM collection_items 
                WHERE collection_id = ? AND item_type = ? 
                AND json_extract(content, '$.url') = ?
            """, (collection_id, item_type, identifier)).fetchone()
            
            return row is not None
    
    def get_duplicate_items(self, collection_id: str) -> List[List[CollectionItem]]:
        """Find duplicate items in a collection."""
        collection = self.get_collection(collection_id)
        if not collection:
            return []
        
        # Group items by content similarity
        duplicates = []
        processed = set()
        
        for i, item in enumerate(collection.items):
            if i in processed:
                continue
                
            similar_items = [item]
            
            for j, other_item in enumerate(collection.items[i+1:], i+1):
                if j in processed:
                    continue
                
                # Check for similarity based on item type
                if self._items_are_similar(item, other_item):
                    similar_items.append(other_item)
                    processed.add(j)
            
            if len(similar_items) > 1:
                duplicates.append(similar_items)
                processed.update(range(i, i + len(similar_items)))
        
        return duplicates
    
    def _items_are_similar(self, item1: CollectionItem, item2: CollectionItem) -> bool:
        """Check if two items are similar (potential duplicates)."""
        if item1.item_type != item2.item_type:
            return False
        
        if item1.item_type == 'image':
            # Compare image URLs
            url1 = item1.content.get('url', '')
            url2 = item2.content.get('url', '')
            return url1 == url2
        
        elif item1.item_type == 'vocabulary':
            # Compare Spanish words
            spanish1 = item1.content.get('spanish', '').lower()
            spanish2 = item2.content.get('spanish', '').lower()
            return spanish1 == spanish2
        
        return False