"""Advanced search functionality with history, filters, and reverse search."""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import quote
import requests
from PIL import Image
import hashlib
import base64
from io import BytesIO


@dataclass
class SearchFilter:
    """Search filter configuration."""
    color: Optional[str] = None  # black_and_white, black, white, yellow, orange, red, purple, magenta, green, teal, blue
    orientation: Optional[str] = None  # landscape, portrait, squarish
    category: Optional[str] = None  # backgrounds, fashion, nature, science, education, feelings, health, people, religion, places, animals, industry, computer, food, sports, transportation, travel, buildings, business, music
    featured: bool = False
    photographer: Optional[str] = None
    collections: List[str] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    safe_search: bool = True
    
    def to_params(self) -> Dict[str, str]:
        """Convert filter to Unsplash API parameters."""
        params = {}
        if self.color:
            params['color'] = self.color
        if self.orientation:
            params['orientation'] = self.orientation
        if self.category:
            params['category'] = self.category
        if self.featured:
            params['featured'] = 'true'
        if self.photographer:
            params['username'] = self.photographer
        if self.collections:
            params['collections'] = ','.join(self.collections)
        if self.min_width:
            params['min_width'] = str(self.min_width)
        if self.min_height:
            params['min_height'] = str(self.min_height)
        return params


@dataclass
class SearchEntry:
    """Search history entry."""
    id: int
    query: str
    timestamp: str
    filters: Dict[str, Any]
    results_count: int
    is_saved: bool = False
    tags: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AdvancedSearchManager:
    """Manages advanced search functionality including history, filters, and reverse search."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "search_history.db"
        self.cache_dir = data_dir / "search_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Language support
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the search history database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    filters TEXT,
                    results_count INTEGER DEFAULT 0,
                    is_saved BOOLEAN DEFAULT FALSE,
                    tags TEXT,
                    notes TEXT DEFAULT '',
                    language TEXT DEFAULT 'en'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    query TEXT NOT NULL,
                    filters TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    use_count INTEGER DEFAULT 0,
                    tags TEXT,
                    notes TEXT DEFAULT ''
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reverse_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    similar_images TEXT,
                    metadata TEXT
                )
            """)
            
            conn.commit()
    
    def add_search_history(self, query: str, filters: SearchFilter, 
                          results_count: int, language: str = 'en') -> int:
        """Add search to history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO search_history 
                (query, timestamp, filters, results_count, language)
                VALUES (?, ?, ?, ?, ?)
            """, (
                query,
                datetime.now().isoformat(),
                json.dumps(asdict(filters)),
                results_count,
                language
            ))
            return cursor.lastrowid
    
    def get_search_history(self, limit: int = 100) -> List[SearchEntry]:
        """Get search history entries."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT id, query, timestamp, filters, results_count, 
                       is_saved, tags, notes
                FROM search_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            
            entries = []
            for row in rows:
                filters_dict = json.loads(row[3]) if row[3] else {}
                tags = json.loads(row[6]) if row[6] else []
                entries.append(SearchEntry(
                    id=row[0],
                    query=row[1],
                    timestamp=row[2],
                    filters=filters_dict,
                    results_count=row[4],
                    is_saved=bool(row[5]),
                    tags=tags,
                    notes=row[7] or ""
                ))
            return entries
    
    def get_autocomplete_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get autocomplete suggestions based on search history."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT DISTINCT query
                FROM search_history 
                WHERE query LIKE ? 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"{partial_query}%", limit)).fetchall()
            
            return [row[0] for row in rows]
    
    def save_search(self, name: str, query: str, filters: SearchFilter, 
                   tags: List[str] = None, notes: str = "") -> bool:
        """Save a search configuration."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO saved_searches 
                    (name, query, filters, created_at, tags, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    query,
                    json.dumps(asdict(filters)),
                    datetime.now().isoformat(),
                    json.dumps(tags or []),
                    notes
                ))
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_saved_searches(self) -> List[Dict[str, Any]]:
        """Get all saved searches."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT name, query, filters, created_at, last_used, 
                       use_count, tags, notes
                FROM saved_searches 
                ORDER BY use_count DESC, created_at DESC
            """).fetchall()
            
            searches = []
            for row in rows:
                filters = json.loads(row[2]) if row[2] else {}
                tags = json.loads(row[6]) if row[6] else []
                searches.append({
                    'name': row[0],
                    'query': row[1],
                    'filters': filters,
                    'created_at': row[3],
                    'last_used': row[4],
                    'use_count': row[5],
                    'tags': tags,
                    'notes': row[7] or ""
                })
            return searches
    
    def use_saved_search(self, name: str) -> Optional[Tuple[str, SearchFilter]]:
        """Use a saved search and update usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT query, filters FROM saved_searches WHERE name = ?
            """, (name,)).fetchone()
            
            if not row:
                return None
            
            # Update usage statistics
            conn.execute("""
                UPDATE saved_searches 
                SET last_used = ?, use_count = use_count + 1
                WHERE name = ?
            """, (datetime.now().isoformat(), name))
            
            filters_dict = json.loads(row[1]) if row[1] else {}
            filters = SearchFilter(**filters_dict)
            return row[0], filters
    
    def delete_saved_search(self, name: str) -> bool:
        """Delete a saved search."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM saved_searches WHERE name = ?", (name,)
            )
            return cursor.rowcount > 0
    
    def translate_query(self, query: str, target_language: str) -> str:
        """Translate search query to target language (placeholder implementation)."""
        # In a real implementation, this would use a translation API
        # For now, return the original query with a language prefix
        if target_language == 'en':
            return query
        
        # Basic translation mapping for common terms
        translations = {
            'es': {
                'sunset': 'puesta de sol',
                'mountain': 'montaña',
                'ocean': 'océano',
                'forest': 'bosque',
                'city': 'ciudad',
                'beach': 'playa',
                'flower': 'flor',
                'cat': 'gato',
                'dog': 'perro',
                'car': 'coche'
            },
            'fr': {
                'sunset': 'coucher de soleil',
                'mountain': 'montagne',
                'ocean': 'océan',
                'forest': 'forêt',
                'city': 'ville',
                'beach': 'plage',
                'flower': 'fleur',
                'cat': 'chat',
                'dog': 'chien',
                'car': 'voiture'
            }
        }
        
        if target_language in translations:
            lang_dict = translations[target_language]
            words = query.lower().split()
            translated_words = [lang_dict.get(word, word) for word in words]
            return ' '.join(translated_words)
        
        return query
    
    def reverse_image_search(self, image_data: bytes, 
                           api_key: str) -> List[Dict[str, Any]]:
        """Perform reverse image search using image similarity."""
        try:
            # Create image hash for caching
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # Check cache first
            cache_file = self.cache_dir / f"reverse_{image_hash}.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cached_result = json.load(f)
                    # Check if cache is less than 24 hours old
                    cache_time = datetime.fromisoformat(cached_result['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=24):
                        return cached_result['results']
            
            # Upload image and search for similar ones
            # This is a simplified implementation - in reality, you'd use 
            # Google Vision API or similar service
            
            # For now, we'll analyze the image and search for similar content
            image = Image.open(BytesIO(image_data))
            
            # Extract basic features (colors, dominant objects)
            # This is a placeholder - real implementation would use ML models
            width, height = image.size
            orientation = 'landscape' if width > height else 'portrait' if height > width else 'squarish'
            
            # Search for images with similar characteristics
            search_terms = self._analyze_image_content(image)
            
            results = []
            for term in search_terms:
                # Use regular Unsplash search with detected terms
                headers = {"Authorization": f"Client-ID {api_key}"}
                params = {
                    'query': term,
                    'orientation': orientation,
                    'per_page': 5
                }
                
                response = requests.get(
                    "https://api.unsplash.com/search/photos",
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for photo in data.get('results', []):
                        results.append({
                            'id': photo['id'],
                            'url': photo['urls']['regular'],
                            'description': photo.get('description', ''),
                            'alt_description': photo.get('alt_description', ''),
                            'similarity_score': 0.7,  # Placeholder
                            'match_type': 'content',
                            'photographer': photo['user']['name'],
                            'tags': [tag['title'] for tag in photo.get('tags', [])]
                        })
            
            # Cache results
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'results': results[:10]  # Limit results
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO reverse_searches 
                    (image_hash, timestamp, similar_images, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    image_hash,
                    datetime.now().isoformat(),
                    json.dumps(results[:10]),
                    json.dumps({'width': width, 'height': height, 'orientation': orientation})
                ))
            
            return results[:10]
            
        except Exception as e:
            print(f"Reverse search error: {e}")
            return []
    
    def _analyze_image_content(self, image: Image.Image) -> List[str]:
        """Analyze image content to extract search terms."""
        # This is a placeholder implementation
        # In a real application, you'd use computer vision APIs
        # like Google Vision, AWS Rekognition, or Azure Computer Vision
        
        # Basic analysis based on image properties
        width, height = image.size
        aspect_ratio = width / height
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Analyze dominant colors
        colors = image.getcolors(maxcolors=256*256*256)
        if colors:
            # Get most common colors
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            dominant_color = sorted_colors[0][1]
            
            # Map RGB to color names
            color_name = self._rgb_to_color_name(dominant_color)
            
            # Generate search terms based on analysis
            terms = []
            
            if aspect_ratio > 1.5:
                terms.extend(['landscape', 'panorama', 'wide view'])
            elif aspect_ratio < 0.7:
                terms.extend(['portrait', 'vertical', 'tall'])
            else:
                terms.extend(['square', 'balanced composition'])
            
            terms.append(color_name)
            
            # Add generic terms based on common photo types
            terms.extend(['nature', 'abstract', 'minimal', 'photography'])
            
            return terms[:5]  # Return top 5 terms
        
        return ['photography', 'image', 'photo']
    
    def _rgb_to_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB values to color name."""
        r, g, b = rgb
        
        # Simple color mapping
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > g and r > b:
            return 'red' if r > 150 else 'brown'
        elif g > r and g > b:
            return 'green'
        elif b > r and b > g:
            return 'blue'
        elif r > 150 and g > 150:
            return 'yellow'
        elif r > 150 and b > 150:
            return 'purple'
        elif g > 150 and b > 150:
            return 'teal'
        else:
            return 'gray'
    
    def get_trending_searches(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending searches from recent history."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT query, COUNT(*) as count, 
                       AVG(results_count) as avg_results,
                       MAX(timestamp) as latest
                FROM search_history 
                WHERE timestamp > ? 
                GROUP BY query 
                HAVING count > 1
                ORDER BY count DESC, avg_results DESC
                LIMIT ?
            """, (cutoff_date, limit)).fetchall()
            
            return [{
                'query': row[0],
                'search_count': row[1],
                'avg_results': int(row[2]),
                'latest_search': row[3]
            } for row in rows]
    
    def export_search_history(self, format_type: str = 'json') -> str:
        """Export search history in specified format."""
        history = self.get_search_history(limit=1000)
        
        if format_type == 'json':
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_searches': len(history),
                'searches': [asdict(entry) for entry in history]
            }
            return json.dumps(data, indent=2)
        
        elif format_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Query', 'Timestamp', 'Results Count', 'Is Saved', 'Tags', 'Notes'])
            
            for entry in history:
                writer.writerow([
                    entry.id,
                    entry.query,
                    entry.timestamp,
                    entry.results_count,
                    entry.is_saved,
                    ', '.join(entry.tags),
                    entry.notes
                ])
            
            return output.getvalue()
        
        return str(history)
    
    def import_search_history(self, data: str, format_type: str = 'json') -> bool:
        """Import search history from external data."""
        try:
            if format_type == 'json':
                imported_data = json.loads(data)
                searches = imported_data.get('searches', [])
                
                with sqlite3.connect(self.db_path) as conn:
                    for search in searches:
                        conn.execute("""
                            INSERT OR IGNORE INTO search_history 
                            (query, timestamp, filters, results_count, is_saved, tags, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            search['query'],
                            search['timestamp'],
                            json.dumps(search.get('filters', {})),
                            search.get('results_count', 0),
                            search.get('is_saved', False),
                            json.dumps(search.get('tags', [])),
                            search.get('notes', '')
                        ))
                return True
        except Exception as e:
            print(f"Import error: {e}")
            return False
    
    def clear_history(self, older_than_days: Optional[int] = None) -> int:
        """Clear search history. If older_than_days is specified, only clear old entries."""
        with sqlite3.connect(self.db_path) as conn:
            if older_than_days:
                cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
                cursor = conn.execute(
                    "DELETE FROM search_history WHERE timestamp < ?", 
                    (cutoff_date,)
                )
            else:
                cursor = conn.execute("DELETE FROM search_history")
            
            return cursor.rowcount