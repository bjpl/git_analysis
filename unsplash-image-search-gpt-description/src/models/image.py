"""
Image data model for managing image search results and metadata.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


class ImageResult:
    """Individual image search result from Unsplash."""
    
    def __init__(self, unsplash_data: Dict[str, Any]):
        self.id = unsplash_data.get('id', '')
        self.description = unsplash_data.get('description', '')
        self.alt_description = unsplash_data.get('alt_description', '')
        self.urls = unsplash_data.get('urls', {})
        self.user = unsplash_data.get('user', {})
        self.width = unsplash_data.get('width', 0)
        self.height = unsplash_data.get('height', 0)
        self.created_at = unsplash_data.get('created_at', '')
        self.likes = unsplash_data.get('likes', 0)
    
    @property
    def regular_url(self) -> str:
        """Get the regular size image URL."""
        return self.urls.get('regular', '')
    
    @property
    def small_url(self) -> str:
        """Get the small size image URL."""
        return self.urls.get('small', '')
    
    @property
    def thumb_url(self) -> str:
        """Get the thumbnail image URL."""
        return self.urls.get('thumb', '')
    
    @property
    def author_name(self) -> str:
        """Get the photographer's name."""
        return self.user.get('name', 'Unknown')
    
    @property
    def author_username(self) -> str:
        """Get the photographer's username."""
        return self.user.get('username', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'description': self.description,
            'alt_description': self.alt_description,
            'urls': self.urls,
            'user': self.user,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at,
            'likes': self.likes
        }


class ImageSearchState:
    """State management for image search pagination and results."""
    
    def __init__(self):
        self.current_query: str = ""
        self.current_page: int = 0
        self.current_results: List[ImageResult] = []
        self.current_index: int = 0
        self.current_image_url: Optional[str] = None
        self.total_results: int = 0
    
    def set_new_search(self, query: str, results_data: Dict[str, Any]):
        """Set up state for a new search query."""
        self.current_query = query
        self.current_page = 1
        self.current_index = 0
        self.current_image_url = None
        
        # Parse results
        results = results_data.get('results', [])
        self.current_results = [ImageResult(result) for result in results]
        self.total_results = results_data.get('total', 0)
    
    def add_page_results(self, results_data: Dict[str, Any]):
        """Add results from a new page."""
        results = results_data.get('results', [])
        new_results = [ImageResult(result) for result in results]
        self.current_results.extend(new_results)
    
    def get_next_image(self) -> Optional[ImageResult]:
        """Get the next image in the current results."""
        if self.current_index < len(self.current_results):
            image = self.current_results[self.current_index]
            self.current_index += 1
            self.current_image_url = image.regular_url
            return image
        return None
    
    def has_more_images(self) -> bool:
        """Check if there are more images in current results."""
        return self.current_index < len(self.current_results)
    
    def increment_page(self):
        """Move to the next page."""
        self.current_page += 1
        self.current_index = 0  # Reset index for new page
    
    def clear_search(self):
        """Clear all search state."""
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        self.total_results = 0
    
    def get_search_info(self) -> Dict[str, Any]:
        """Get current search information."""
        return {
            'query': self.current_query,
            'page': self.current_page,
            'current_index': self.current_index,
            'results_count': len(self.current_results),
            'total_results': self.total_results,
            'has_more': self.has_more_images()
        }