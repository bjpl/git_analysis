"""
Enhanced session tracking module for managing search history and image variety.
Ensures different images are shown for the same search term across sessions.
"""

import json
import random
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
import os


@dataclass
class ImageRecord:
    """Record of a shown image."""
    url: str
    search_query: str
    timestamp: float
    page_number: int
    index_in_page: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class SearchSession:
    """Record of a search session."""
    query: str
    timestamp: float
    images_shown: List[str]
    page_numbers_used: List[int]
    total_results_seen: int
    
    def to_dict(self):
        return asdict(self)


class SessionTracker:
    """
    Tracks search sessions and ensures image variety across searches.
    Uses different strategies to show different images for repeated searches.
    """
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize the session tracker.
        
        Args:
            data_dir: Directory to store session data
        """
        self.data_dir = data_dir or Path("./data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.data_dir / "search_sessions.json"
        self.image_history_file = self.data_dir / "image_history.json"
        
        # In-memory caches
        self.search_history: Dict[str, SearchSession] = {}
        self.image_history: Dict[str, List[ImageRecord]] = {}
        self.current_session_id = None
        
        # Configuration
        self.max_history_days = 30  # Keep history for 30 days
        self.max_images_per_query = 100  # Track up to 100 images per query
        self.shuffle_seed_interval = 3600  # Change shuffle seed every hour
        
        # Load existing data
        self.load_session_data()
    
    def load_session_data(self):
        """Load session data from disk."""
        # Load search history
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    for query, session_data in data.items():
                        self.search_history[query] = SearchSession(**session_data)
            except (json.JSONDecodeError, TypeError):
                self.search_history = {}
        
        # Load image history
        if self.image_history_file.exists():
            try:
                with open(self.image_history_file, 'r') as f:
                    data = json.load(f)
                    for query, records in data.items():
                        self.image_history[query] = [
                            ImageRecord(**record) for record in records
                        ]
            except (json.JSONDecodeError, TypeError):
                self.image_history = {}
        
        # Clean old data
        self.cleanup_old_data()
    
    def save_session_data(self):
        """Save session data to disk."""
        # Save search history
        search_data = {
            query: session.to_dict() 
            for query, session in self.search_history.items()
        }
        with open(self.session_file, 'w') as f:
            json.dump(search_data, f, indent=2)
        
        # Save image history
        image_data = {
            query: [record.to_dict() for record in records]
            for query, records in self.image_history.items()
        }
        with open(self.image_history_file, 'w') as f:
            json.dump(image_data, f, indent=2)
    
    def cleanup_old_data(self):
        """Remove data older than max_history_days."""
        cutoff_time = time.time() - (self.max_history_days * 24 * 3600)
        
        # Clean search history
        self.search_history = {
            query: session for query, session in self.search_history.items()
            if session.timestamp > cutoff_time
        }
        
        # Clean image history
        for query in list(self.image_history.keys()):
            self.image_history[query] = [
                record for record in self.image_history.get(query, [])
                if record.timestamp > cutoff_time
            ]
            if not self.image_history[query]:
                del self.image_history[query]
    
    def get_search_parameters(self, query: str) -> Dict[str, any]:
        """
        Get optimized search parameters for a query to ensure variety.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with search parameters (page, per_page, offset strategy)
        """
        query_lower = query.lower().strip()
        
        # Get or create session
        if query_lower not in self.search_history:
            self.search_history[query_lower] = SearchSession(
                query=query_lower,
                timestamp=time.time(),
                images_shown=[],
                page_numbers_used=[],
                total_results_seen=0
            )
        
        session = self.search_history[query_lower]
        shown_images = set(session.images_shown)
        
        # Strategy 1: Use different page numbers
        used_pages = set(session.page_numbers_used)
        
        # Calculate optimal page based on history
        if len(shown_images) < 10:
            # First few searches: use random pages 1-5
            available_pages = [p for p in range(1, 6) if p not in used_pages]
            if available_pages:
                page = random.choice(available_pages)
            else:
                page = random.randint(1, 5)
        elif len(shown_images) < 30:
            # Medium searches: expand to pages 1-10
            available_pages = [p for p in range(1, 11) if p not in used_pages]
            if available_pages:
                page = random.choice(available_pages)
            else:
                page = random.randint(6, 15)
        else:
            # Many searches: use advanced pagination
            page = self._calculate_advanced_page(query_lower, shown_images)
        
        # Strategy 2: Use time-based seed for consistent randomization
        time_seed = int(time.time() / self.shuffle_seed_interval)
        random.seed(hash(query_lower) + time_seed)
        
        # Strategy 3: Vary results per page
        per_page = random.choice([10, 15, 20, 30])
        
        # Update session
        if page not in session.page_numbers_used:
            session.page_numbers_used.append(page)
        
        # Save state
        self.save_session_data()
        
        return {
            "page": page,
            "per_page": per_page,
            "shuffle_seed": time_seed,
            "shown_count": len(shown_images),
            "strategy": self._get_strategy_name(len(shown_images))
        }
    
    def _calculate_advanced_page(self, query: str, shown_images: Set[str]) -> int:
        """
        Calculate an advanced page number for queries with many shown images.
        
        Args:
            query: The search query
            shown_images: Set of already shown image URLs
            
        Returns:
            Optimized page number
        """
        # Use hash-based distribution for consistency
        query_hash = hashlib.md5(query.encode()).hexdigest()
        base_page = int(query_hash[:4], 16) % 20 + 1
        
        # Add time-based offset
        time_offset = int(time.time() / 3600) % 10
        
        # Calculate final page
        page = base_page + time_offset + (len(shown_images) // 10)
        
        return min(page, 100)  # Cap at page 100
    
    def _get_strategy_name(self, shown_count: int) -> str:
        """Get the name of the current variety strategy."""
        if shown_count < 10:
            return "exploring"
        elif shown_count < 30:
            return "expanding"
        else:
            return "deep_search"
    
    def record_shown_image(self, query: str, image_url: str, page: int = 1, index: int = 0):
        """
        Record that an image has been shown.
        
        Args:
            query: The search query
            image_url: URL of the shown image
            page: Page number the image came from
            index: Index within the page
        """
        query_lower = query.lower().strip()
        
        # Update search history
        if query_lower in self.search_history:
            session = self.search_history[query_lower]
            if image_url not in session.images_shown:
                session.images_shown.append(image_url)
                session.total_results_seen += 1
            
            # Limit stored images
            if len(session.images_shown) > self.max_images_per_query:
                session.images_shown = session.images_shown[-self.max_images_per_query:]
        
        # Update image history
        if query_lower not in self.image_history:
            self.image_history[query_lower] = []
        
        record = ImageRecord(
            url=image_url,
            search_query=query_lower,
            timestamp=time.time(),
            page_number=page,
            index_in_page=index
        )
        
        self.image_history[query_lower].append(record)
        
        # Limit history size
        if len(self.image_history[query_lower]) > self.max_images_per_query:
            self.image_history[query_lower] = self.image_history[query_lower][-self.max_images_per_query:]
        
        # Save state
        self.save_session_data()
    
    def get_shown_images_for_query(self, query: str) -> List[str]:
        """
        Get list of image URLs already shown for a query.
        
        Args:
            query: The search query
            
        Returns:
            List of image URLs
        """
        query_lower = query.lower().strip()
        if query_lower in self.search_history:
            return self.search_history[query_lower].images_shown.copy()
        return []
    
    def reset_query_history(self, query: str):
        """
        Reset history for a specific query to get fresh results.
        
        Args:
            query: The search query to reset
        """
        query_lower = query.lower().strip()
        
        if query_lower in self.search_history:
            del self.search_history[query_lower]
        
        if query_lower in self.image_history:
            del self.image_history[query_lower]
        
        self.save_session_data()
    
    def get_statistics(self) -> Dict[str, any]:
        """Get session statistics."""
        total_searches = len(self.search_history)
        total_images = sum(
            len(session.images_shown) 
            for session in self.search_history.values()
        )
        
        # Find most searched terms
        most_searched = sorted(
            self.search_history.items(),
            key=lambda x: len(x[1].images_shown),
            reverse=True
        )[:5]
        
        return {
            "total_searches": total_searches,
            "total_images_shown": total_images,
            "unique_queries": list(self.search_history.keys()),
            "most_searched": [
                {"query": q, "images": len(s.images_shown)} 
                for q, s in most_searched
            ],
            "data_size_mb": self._calculate_data_size()
        }
    
    def _calculate_data_size(self) -> float:
        """Calculate the size of stored data in MB."""
        size = 0
        if self.session_file.exists():
            size += self.session_file.stat().st_size
        if self.image_history_file.exists():
            size += self.image_history_file.stat().st_size
        return size / (1024 * 1024)
    
    def export_history(self, filepath: Path):
        """Export complete history to a file."""
        export_data = {
            "search_history": {
                q: s.to_dict() for q, s in self.search_history.items()
            },
            "image_history": {
                q: [r.to_dict() for r in records]
                for q, records in self.image_history.items()
            },
            "statistics": self.get_statistics(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)