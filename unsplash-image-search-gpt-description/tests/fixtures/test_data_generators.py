"""
Test data generators for image collection testing.
Provides realistic test data, mock responses, and edge case scenarios.
"""

import json
import random
import string
import time
from typing import Dict, List, Any, Generator
from pathlib import Path
import base64
from datetime import datetime, timedelta


class UnsplashResponseGenerator:
    """Generate realistic Unsplash API responses for testing."""

    @staticmethod
    def create_search_response(
        query: str,
        page: int = 1,
        per_page: int = 10,
        total_results: int = 1000
    ) -> Dict[str, Any]:
        """Generate a realistic Unsplash search response."""
        results = []
        
        for i in range(per_page):
            image_id = f"test_img_{query}_{page}_{i}_{int(time.time())}"
            results.append({
                "id": image_id,
                "slug": f"{query}-{i}",
                "created_at": datetime.now().isoformat() + "Z",
                "updated_at": datetime.now().isoformat() + "Z",
                "promoted_at": None,
                "width": random.randint(800, 4000),
                "height": random.randint(600, 3000),
                "color": f"#{random.randint(0, 16777215):06x}",
                "blur_hash": f"L{random.randint(100000, 999999):06d}",
                "description": f"A beautiful {query} image for testing",
                "alt_description": f"Test {query} image {i}",
                "urls": {
                    "raw": f"https://images.unsplash.com/photo-{image_id}?ixlib=rb-4.0.3",
                    "full": f"https://images.unsplash.com/photo-{image_id}?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb",
                    "regular": f"https://images.unsplash.com/photo-{image_id}?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&w=1080",
                    "small": f"https://images.unsplash.com/photo-{image_id}?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&w=400",
                    "thumb": f"https://images.unsplash.com/photo-{image_id}?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&w=200",
                    "small_s3": f"https://s3.us-west-2.amazonaws.com/images.unsplash.com/small/photo-{image_id}"
                },
                "links": {
                    "self": f"https://api.unsplash.com/photos/{image_id}",
                    "html": f"https://unsplash.com/photos/{image_id}",
                    "download": f"https://unsplash.com/photos/{image_id}/download?ixid=test",
                    "download_location": f"https://api.unsplash.com/photos/{image_id}/download?ixid=test"
                },
                "categories": [],
                "likes": random.randint(0, 1000),
                "liked_by_user": False,
                "current_user_collections": [],
                "sponsorship": None,
                "topic_submissions": {},
                "user": UnsplashResponseGenerator._create_test_user(i)
            })
        
        total_pages = (total_results + per_page - 1) // per_page
        
        return {
            "total": total_results,
            "total_pages": total_pages,
            "results": results
        }

    @staticmethod
    def _create_test_user(index: int) -> Dict[str, Any]:
        """Create a test user object."""
        username = f"testuser{index}"
        return {
            "id": f"user_{index}_{int(time.time())}",
            "updated_at": datetime.now().isoformat() + "Z",
            "username": username,
            "name": f"Test User {index}",
            "first_name": "Test",
            "last_name": f"User{index}",
            "twitter_username": f"test_user_{index}",
            "portfolio_url": f"https://example.com/{username}",
            "bio": f"Test user {index} for testing purposes",
            "location": "Test City",
            "links": {
                "self": f"https://api.unsplash.com/users/{username}",
                "html": f"https://unsplash.com/@{username}",
                "photos": f"https://api.unsplash.com/users/{username}/photos",
                "likes": f"https://api.unsplash.com/users/{username}/likes",
                "portfolio": f"https://api.unsplash.com/users/{username}/portfolio",
                "following": f"https://api.unsplash.com/users/{username}/following",
                "followers": f"https://api.unsplash.com/users/{username}/followers"
            },
            "profile_image": {
                "small": f"https://images.unsplash.com/profile-{index}?ixlib=rb-4.0.3&crop=faces&fit=crop&w=32&h=32",
                "medium": f"https://images.unsplash.com/profile-{index}?ixlib=rb-4.0.3&crop=faces&fit=crop&w=64&h=64",
                "large": f"https://images.unsplash.com/profile-{index}?ixlib=rb-4.0.3&crop=faces&fit=crop&w=128&h=128"
            },
            "instagram_username": f"test_insta_{index}",
            "total_collections": random.randint(0, 50),
            "total_likes": random.randint(0, 1000),
            "total_photos": random.randint(10, 500),
            "accepted_tos": True,
            "for_hire": random.choice([True, False]),
            "social": {
                "instagram_username": f"test_insta_{index}",
                "portfolio_url": f"https://example.com/{username}",
                "twitter_username": f"test_user_{index}",
                "paypal_email": None
            }
        }

    @staticmethod
    def create_empty_response() -> Dict[str, Any]:
        """Create an empty search response."""
        return {
            "total": 0,
            "total_pages": 0,
            "results": []
        }

    @staticmethod
    def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "errors": [message]
        }


class ImageDataGenerator:
    """Generate test image data for testing."""

    @staticmethod
    def create_test_image_data(width: int = 100, height: int = 100, format: str = "PNG") -> bytes:
        """Create test image data."""
        from PIL import Image
        import io
        
        # Create a simple test image
        image = Image.new("RGB", (width, height), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # Add some pattern
        pixels = image.load()
        for i in range(width):
            for j in range(height):
                if (i + j) % 10 == 0:
                    pixels[i, j] = (255, 255, 255)  # White dots
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    @staticmethod
    def create_corrupted_image_data() -> bytes:
        """Create corrupted image data for error testing."""
        return b"This is not a valid image file"

    @staticmethod
    def create_large_image_data(size_mb: int = 5) -> bytes:
        """Create large image data for memory testing."""
        # Create approximately the requested size in MB
        data_size = size_mb * 1024 * 1024
        return b"x" * data_size


class ScenarioGenerator:
    """Generate test scenarios for comprehensive testing."""

    @staticmethod
    def create_search_scenarios() -> List[Dict[str, Any]]:
        """Create various search scenarios."""
        scenarios = [
            # Normal cases
            {"query": "nature", "expected_results": 10, "description": "Normal search"},
            {"query": "mountains", "expected_results": 8, "description": "Popular query"},
            {"query": "sunset", "expected_results": 15, "description": "High-result query"},
            
            # Edge cases
            {"query": "", "expected_results": 0, "description": "Empty query"},
            {"query": "   ", "expected_results": 0, "description": "Whitespace query"},
            {"query": "nonexistentquery12345", "expected_results": 0, "description": "No results"},
            
            # Special characters
            {"query": "café", "expected_results": 5, "description": "Accented characters"},
            {"query": "中文", "expected_results": 3, "description": "Chinese characters"},
            {"query": "emoji 🌟", "expected_results": 7, "description": "Emoji in query"},
            {"query": '"quoted search"', "expected_results": 4, "description": "Quoted search"},
            
            # Long queries
            {"query": "very " * 50 + "long query", "expected_results": 2, "description": "Very long query"},
            
            # Special symbols
            {"query": "@#$%^&*()", "expected_results": 0, "description": "Special symbols"},
            {"query": "search & replace", "expected_results": 6, "description": "Ampersand"},
            {"query": "100% natural", "expected_results": 8, "description": "Percentage symbol"}
        ]
        
        return scenarios

    @staticmethod
    def create_error_scenarios() -> List[Dict[str, Any]]:
        """Create error scenarios for testing."""
        return [
            {
                "error_type": "connection_error",
                "exception": "requests.exceptions.ConnectionError",
                "message": "Failed to establish connection",
                "should_retry": True
            },
            {
                "error_type": "timeout",
                "exception": "requests.exceptions.Timeout",
                "message": "Request timed out",
                "should_retry": True
            },
            {
                "error_type": "http_401",
                "exception": "requests.exceptions.HTTPError",
                "message": "401 Client Error: Unauthorized",
                "should_retry": False
            },
            {
                "error_type": "http_403",
                "exception": "requests.exceptions.HTTPError", 
                "message": "403 Client Error: Forbidden",
                "should_retry": False
            },
            {
                "error_type": "http_429",
                "exception": "requests.exceptions.HTTPError",
                "message": "429 Client Error: Too Many Requests",
                "should_retry": True
            },
            {
                "error_type": "http_500",
                "exception": "requests.exceptions.HTTPError",
                "message": "500 Internal Server Error",
                "should_retry": True
            },
            {
                "error_type": "json_decode",
                "exception": "json.JSONDecodeError",
                "message": "Invalid JSON response",
                "should_retry": False
            }
        ]

    @staticmethod
    def create_performance_scenarios() -> List[Dict[str, Any]]:
        """Create performance testing scenarios."""
        return [
            {
                "name": "small_dataset",
                "image_count": 10,
                "page_size": 10,
                "expected_time": 1.0,
                "memory_limit_mb": 50
            },
            {
                "name": "medium_dataset", 
                "image_count": 100,
                "page_size": 10,
                "expected_time": 5.0,
                "memory_limit_mb": 100
            },
            {
                "name": "large_dataset",
                "image_count": 500,
                "page_size": 20,
                "expected_time": 15.0,
                "memory_limit_mb": 200
            },
            {
                "name": "stress_test",
                "image_count": 1000,
                "page_size": 50,
                "expected_time": 30.0,
                "memory_limit_mb": 300
            }
        ]


class SessionDataGenerator:
    """Generate realistic session data for testing."""

    @staticmethod
    def create_session_data(
        session_count: int = 1,
        entries_per_session: int = 5
    ) -> Dict[str, Any]:
        """Create realistic session data."""
        sessions = []
        
        for session_idx in range(session_count):
            session_start = datetime.now() - timedelta(days=random.randint(0, 30))
            session_end = session_start + timedelta(minutes=random.randint(15, 120))
            
            entries = []
            for entry_idx in range(entries_per_session):
                entry_time = session_start + timedelta(
                    minutes=random.randint(0, int((session_end - session_start).total_seconds() / 60))
                )
                
                entries.append({
                    "timestamp": entry_time.isoformat(),
                    "query": random.choice(["nature", "architecture", "people", "animals", "food"]),
                    "image_url": f"https://images.unsplash.com/photo-{random.randint(100000, 999999)}",
                    "user_note": f"Test note {entry_idx} for session {session_idx}",
                    "generated_description": f"Generated description {entry_idx} for testing purposes"
                })
            
            vocabulary_words = [
                "la montaña - mountain",
                "el río - river", 
                "hermoso - beautiful",
                "verde - green",
                "el cielo - sky"
            ]
            
            sessions.append({
                "session_start": session_start.isoformat(),
                "session_end": session_end.isoformat(),
                "entries": entries,
                "vocabulary_learned": len(vocabulary_words),
                "target_phrases": random.sample(vocabulary_words, min(len(vocabulary_words), random.randint(2, 5)))
            })
        
        return {"sessions": sessions}

    @staticmethod
    def create_vocabulary_data(word_count: int = 50) -> List[Dict[str, str]]:
        """Create test vocabulary data."""
        spanish_words = [
            "casa", "perro", "gato", "árbol", "flor", "agua", "fuego", "tierra", "cielo", "sol",
            "luna", "estrella", "montaña", "río", "mar", "bosque", "jardín", "ciudad", "pueblo", "coche",
            "bicicleta", "avión", "tren", "barco", "libro", "papel", "lápiz", "mesa", "silla", "cama",
            "ventana", "puerta", "techo", "pared", "suelo", "escalera", "cocina", "baño", "dormitorio", "salón",
            "comida", "bebida", "pan", "leche", "carne", "pescado", "fruta", "verdura", "arroz", "pasta"
        ]
        
        english_words = [
            "house", "dog", "cat", "tree", "flower", "water", "fire", "earth", "sky", "sun",
            "moon", "star", "mountain", "river", "sea", "forest", "garden", "city", "town", "car",
            "bicycle", "plane", "train", "boat", "book", "paper", "pencil", "table", "chair", "bed",
            "window", "door", "roof", "wall", "floor", "stairs", "kitchen", "bathroom", "bedroom", "living room",
            "food", "drink", "bread", "milk", "meat", "fish", "fruit", "vegetable", "rice", "pasta"
        ]
        
        vocabulary = []
        for i in range(min(word_count, len(spanish_words))):
            vocabulary.append({
                "Spanish": spanish_words[i],
                "English": english_words[i],
                "Date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M"),
                "Search Query": random.choice(["nature", "food", "animals", "architecture"]),
                "Image URL": f"https://images.unsplash.com/photo-{random.randint(100000, 999999)}",
                "Context": f"Context for {spanish_words[i]}"
            })
        
        return vocabulary


class ConfigurationGenerator:
    """Generate test configurations for different scenarios."""

    @staticmethod
    def create_test_config(scenario: str = "default") -> Dict[str, Any]:
        """Create test configuration for different scenarios."""
        base_config = {
            "API": {
                "unsplash_access_key": "test_unsplash_key_123456789",
                "openai_api_key": "sk-test_openai_key_123456789",
                "gpt_model": "gpt-4o-mini"
            },
            "Paths": {
                "data_dir": "/tmp/test_data",
                "log_file": "/tmp/test_data/session_log.json",
                "vocabulary_file": "/tmp/test_data/vocabulary.csv"
            },
            "UI": {
                "window_width": "1100",
                "window_height": "800",
                "font_size": "12",
                "theme": "light",
                "zoom_level": "100"
            },
            "Search": {
                "max_images_per_search": "30",
                "show_progress_counter": "true",
                "enable_search_limits": "true"
            }
        }

        if scenario == "high_volume":
            base_config["Search"]["max_images_per_search"] = "100"
        elif scenario == "low_memory":
            base_config["Search"]["max_images_per_search"] = "10"
        elif scenario == "performance":
            base_config["Search"]["max_images_per_search"] = "50"
            base_config["UI"]["theme"] = "dark"

        return base_config

    @staticmethod
    def create_invalid_config() -> Dict[str, Any]:
        """Create invalid configuration for error testing."""
        return {
            "API": {
                "unsplash_access_key": "",  # Invalid: empty key
                "openai_api_key": "invalid_key",  # Invalid: wrong format
                "gpt_model": "nonexistent-model"  # Invalid: doesn't exist
            },
            "Paths": {
                "data_dir": "/nonexistent/path",  # Invalid: doesn't exist
                "log_file": "",  # Invalid: empty
                "vocabulary_file": None  # Invalid: None
            }
        }


class MockResponseGenerator:
    """Generate mock HTTP responses for testing."""

    @staticmethod
    def create_success_response(data: Dict[str, Any]) -> Any:
        """Create a successful mock response."""
        from unittest.mock import Mock
        
        response = Mock()
        response.status_code = 200
        response.json.return_value = data
        response.raise_for_status = Mock()
        response.headers = {"Content-Type": "application/json"}
        return response

    @staticmethod
    def create_error_response(status_code: int, message: str) -> Any:
        """Create an error mock response."""
        from unittest.mock import Mock
        import requests
        
        response = Mock()
        response.status_code = status_code
        response.json.return_value = {"error": message}
        
        if status_code >= 400:
            response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{status_code} {message}")
        else:
            response.raise_for_status = Mock()
            
        return response

    @staticmethod
    def create_timeout_response() -> Any:
        """Create a timeout response."""
        from unittest.mock import Mock
        import requests
        
        response = Mock()
        response.side_effect = requests.exceptions.Timeout("Request timed out")
        return response


# Export generators for easy import
__all__ = [
    'UnsplashResponseGenerator',
    'ImageDataGenerator', 
    'ScenarioGenerator',
    'SessionDataGenerator',
    'ConfigurationGenerator',
    'MockResponseGenerator'
]