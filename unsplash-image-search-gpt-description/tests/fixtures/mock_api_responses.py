"""
Mock API responses and fixtures for comprehensive testing.
Provides realistic Unsplash and OpenAI API response data.
"""

import json
from datetime import datetime
from typing import Dict, List, Any


class MockUnsplashAPI:
    """Mock Unsplash API responses for testing."""
    
    @staticmethod
    def successful_search_response(page: int = 1, per_page: int = 10, query: str = "test") -> Dict[str, Any]:
        """Generate a successful search response."""
        base_results = [
            {
                "id": f"test_image_{i + (page-1) * per_page}",
                "slug": f"test-image-{i}",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "promoted_at": None,
                "width": 4000,
                "height": 3000,
                "color": "#0c0c0c",
                "blur_hash": "LEHV6nWB2yk8pyo0adR*.7kCMdnj",
                "description": f"A beautiful {query} image {i}",
                "alt_description": f"Test {query} image number {i}",
                "urls": {
                    "raw": f"https://images.unsplash.com/photo-{i + (page-1) * per_page}?ixid=raw",
                    "full": f"https://images.unsplash.com/photo-{i + (page-1) * per_page}?ixid=full",
                    "regular": f"https://images.unsplash.com/photo-{i + (page-1) * per_page}?w=1080",
                    "small": f"https://images.unsplash.com/photo-{i + (page-1) * per_page}?w=400",
                    "thumb": f"https://images.unsplash.com/photo-{i + (page-1) * per_page}?w=200"
                },
                "links": {
                    "self": f"https://api.unsplash.com/photos/test_image_{i}",
                    "html": f"https://unsplash.com/photos/test_image_{i}",
                    "download": f"https://unsplash.com/photos/test_image_{i}/download",
                    "download_location": f"https://api.unsplash.com/photos/test_image_{i}/download"
                },
                "categories": [],
                "likes": 100 + i * 10,
                "liked_by_user": False,
                "current_user_collections": [],
                "sponsorship": None,
                "topic_submissions": {},
                "user": {
                    "id": f"user_{i}",
                    "updated_at": "2024-01-01T12:00:00Z",
                    "username": f"photographer_{i}",
                    "name": f"Test Photographer {i}",
                    "first_name": "Test",
                    "last_name": f"Photographer {i}",
                    "twitter_username": f"photo_{i}",
                    "portfolio_url": f"https://example.com/portfolio_{i}",
                    "bio": f"Professional {query} photographer",
                    "location": "Test City",
                    "links": {
                        "self": f"https://api.unsplash.com/users/photographer_{i}",
                        "html": f"https://unsplash.com/@photographer_{i}",
                        "photos": f"https://api.unsplash.com/users/photographer_{i}/photos",
                        "likes": f"https://api.unsplash.com/users/photographer_{i}/likes",
                        "portfolio": f"https://api.unsplash.com/users/photographer_{i}/portfolio",
                        "following": f"https://api.unsplash.com/users/photographer_{i}/following",
                        "followers": f"https://api.unsplash.com/users/photographer_{i}/followers"
                    },
                    "profile_image": {
                        "small": f"https://images.unsplash.com/profile-{i}?w=32",
                        "medium": f"https://images.unsplash.com/profile-{i}?w=64",
                        "large": f"https://images.unsplash.com/profile-{i}?w=128"
                    },
                    "instagram_username": f"photo_{i}",
                    "total_collections": 5,
                    "total_likes": 1000,
                    "total_photos": 500,
                    "accepted_tos": True,
                    "for_hire": True,
                    "social": {
                        "instagram_username": f"photo_{i}",
                        "portfolio_url": f"https://example.com/portfolio_{i}",
                        "twitter_username": f"photo_{i}",
                        "paypal_email": None
                    }
                },
                "tags": [
                    {"type": "landing_page", "title": query},
                    {"type": "regular", "title": "beautiful"},
                    {"type": "regular", "title": "nature"}
                ]
            }
            for i in range(1, min(per_page + 1, 11))  # Max 10 results per page
        ]
        
        total_results = 500  # Simulate large result set
        total_pages = total_results // per_page
        
        return {
            "total": total_results,
            "total_pages": total_pages,
            "results": base_results
        }
    
    @staticmethod
    def empty_search_response() -> Dict[str, Any]:
        """Generate an empty search response."""
        return {
            "total": 0,
            "total_pages": 0,
            "results": []
        }
    
    @staticmethod
    def rate_limited_error() -> Dict[str, Any]:
        """Generate a rate limit error response."""
        return {
            "errors": ["Rate Limit Exceeded"]
        }
    
    @staticmethod
    def unauthorized_error() -> Dict[str, Any]:
        """Generate an unauthorized error response."""
        return {
            "errors": ["OAuth error: The access token is invalid"]
        }
    
    @staticmethod
    def large_result_set(query: str = "popular", total: int = 10000) -> Dict[str, Any]:
        """Generate a response with very large result set."""
        per_page = 30
        results = []
        
        for i in range(per_page):
            results.append({
                "id": f"popular_image_{i}",
                "urls": {
                    "regular": f"https://images.unsplash.com/popular-{i}?w=1080",
                    "small": f"https://images.unsplash.com/popular-{i}?w=400"
                },
                "alt_description": f"Popular {query} image {i}",
                "description": f"Very popular {query} content",
                "user": {"name": f"Popular Photographer {i}"},
                "likes": 5000 + i * 100
            })
        
        return {
            "total": total,
            "total_pages": total // per_page,
            "results": results
        }


class MockOpenAIAPI:
    """Mock OpenAI API responses for testing."""
    
    @staticmethod
    def successful_description_response(content: str = None) -> Dict[str, Any]:
        """Generate a successful GPT description response."""
        if content is None:
            content = ("Esta es una hermosa imagen que muestra un paisaje natural. "
                      "Se puede ver una montaña majestuosa al fondo, con un lago cristalino "
                      "en el centro de la composición. Los árboles verdes rodean el área, "
                      "creando un ambiente muy tranquilo y sereno.")
        
        return {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": 1699474800,
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 50,
                "total_tokens": 200
            }
        }
    
    @staticmethod
    def successful_extraction_response() -> Dict[str, Any]:
        """Generate a successful vocabulary extraction response."""
        extraction_content = json.dumps({
            "Sustantivos": [
                "la montaña",
                "el lago",
                "los árboles",
                "el paisaje",
                "el ambiente"
            ],
            "Verbos": [
                "muestra",
                "puede ver",
                "rodean",
                "creando"
            ],
            "Adjetivos": [
                "hermosa",
                "natural",
                "majestuosa",
                "cristalino",
                "verdes",
                "tranquilo",
                "sereno"
            ],
            "Adverbios": [
                "muy"
            ],
            "Frases clave": [
                "paisaje natural",
                "muy tranquilo",
                "lago cristalino",
                "montaña majestuosa"
            ]
        })
        
        return MockOpenAIAPI.successful_description_response(extraction_content)
    
    @staticmethod
    def successful_translation_response(spanish_word: str, english_translation: str = None) -> Dict[str, Any]:
        """Generate a successful translation response."""
        if english_translation is None:
            translations = {
                "la montaña": "the mountain",
                "el lago": "the lake",
                "los árboles": "the trees",
                "hermosa": "beautiful",
                "natural": "natural",
                "tranquilo": "peaceful",
                "paisaje natural": "natural landscape"
            }
            english_translation = translations.get(spanish_word, f"translation of {spanish_word}")
        
        return MockOpenAIAPI.successful_description_response(english_translation)
    
    @staticmethod
    def rate_limited_error() -> Dict[str, Any]:
        """Generate a rate limit error response."""
        return {
            "error": {
                "message": "Rate limit reached for requests",
                "type": "rate_limit_error",
                "param": None,
                "code": "rate_limit_exceeded"
            }
        }
    
    @staticmethod
    def invalid_api_key_error() -> Dict[str, Any]:
        """Generate an invalid API key error response."""
        return {
            "error": {
                "message": "Invalid API key provided",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_api_key"
            }
        }
    
    @staticmethod
    def quota_exceeded_error() -> Dict[str, Any]:
        """Generate a quota exceeded error response."""
        return {
            "error": {
                "message": "You exceeded your current quota",
                "type": "insufficient_quota",
                "param": None,
                "code": "insufficient_quota"
            }
        }
    
    @staticmethod
    def malformed_json_response() -> str:
        """Generate malformed JSON for testing parsing errors."""
        return '{"Sustantivos": ["la montaña", "el lago",], "Verbos": [}'  # Invalid JSON
    
    @staticmethod
    def empty_extraction_response() -> Dict[str, Any]:
        """Generate empty extraction response."""
        return MockOpenAIAPI.successful_description_response('{}')


class MockImageData:
    """Mock image data for testing."""
    
    @staticmethod
    def valid_png_bytes() -> bytes:
        """Generate valid PNG image bytes (1x1 transparent PNG)."""
        return (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
                b'\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\xcc'
                b'\xdb\xd2\x00\x00\x00\x00IEND\xaeB`\x82')
    
    @staticmethod
    def valid_jpg_bytes() -> bytes:
        """Generate minimal valid JPEG bytes."""
        return (b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H'
                b'\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07'
                b'\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13'
                b'\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c'
                b'(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00'
                b'\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00'
                b'\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff'
                b'\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9')
    
    @staticmethod
    def corrupted_image_bytes() -> bytes:
        """Generate corrupted image bytes."""
        return b'corrupted_not_an_image_file_data_123456789'
    
    @staticmethod
    def large_image_bytes() -> bytes:
        """Generate large image data (simulated)."""
        # Create a PNG with large dimensions in header
        png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        # Width and height as 32-bit big-endian (simulate 8000x6000)
        dimensions = b'\x00\x00\x1f@\x00\x00\x17p'  # 8000x6000
        png_rest = (b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0c'
                   b'IDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\xcc\xdb'
                   b'\xd2\x00\x00\x00\x00IEND\xaeB`\x82')
        return png_header + dimensions + png_rest


class MockSessionData:
    """Mock session data for testing persistence."""
    
    @staticmethod
    def sample_session_log() -> Dict[str, Any]:
        """Generate sample session log data."""
        return {
            "sessions": [
                {
                    "session_start": "2024-01-01T10:00:00",
                    "session_end": "2024-01-01T10:30:00",
                    "entries": [
                        {
                            "timestamp": "2024-01-01T10:05:00",
                            "query": "nature",
                            "image_url": "https://images.unsplash.com/photo-1",
                            "user_note": "Beautiful mountain landscape",
                            "generated_description": "Esta es una hermosa montaña."
                        },
                        {
                            "timestamp": "2024-01-01T10:15:00",
                            "query": "forest",
                            "image_url": "https://images.unsplash.com/photo-2",
                            "user_note": "Dense forest path",
                            "generated_description": "Un sendero en el bosque."
                        }
                    ],
                    "vocabulary_learned": 8,
                    "target_phrases": [
                        "la montaña - the mountain",
                        "hermosa - beautiful",
                        "el bosque - the forest",
                        "el sendero - the path"
                    ]
                }
            ]
        }
    
    @staticmethod
    def sample_vocabulary_csv_data() -> List[List[str]]:
        """Generate sample vocabulary CSV data."""
        return [
            ['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'],
            ['la montaña', 'the mountain', '2024-01-01 10:05', 'nature', 'https://images.unsplash.com/photo-1', 'hermosa montaña'],
            ['hermosa', 'beautiful', '2024-01-01 10:06', 'nature', 'https://images.unsplash.com/photo-1', 'imagen hermosa'],
            ['el bosque', 'the forest', '2024-01-01 10:15', 'forest', 'https://images.unsplash.com/photo-2', 'bosque denso'],
            ['el sendero', 'the path', '2024-01-01 10:16', 'forest', 'https://images.unsplash.com/photo-2', 'sendero del bosque']
        ]


class MockNetworkScenarios:
    """Mock network condition scenarios for testing."""
    
    @staticmethod
    def slow_response_simulation(delay: float = 2.0):
        """Simulate slow network response."""
        import time
        time.sleep(delay)
        return MockUnsplashAPI.successful_search_response()
    
    @staticmethod
    def intermittent_failure_simulation(failure_count: int = 2):
        """Simulate intermittent network failures."""
        call_count = 0
        
        def simulate_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= failure_count:
                raise ConnectionError("Network temporarily unavailable")
            return MockUnsplashAPI.successful_search_response()
        
        return simulate_call
    
    @staticmethod
    def timeout_simulation():
        """Simulate network timeout."""
        import requests
        raise requests.exceptions.Timeout("Request timed out")
    
    @staticmethod
    def dns_failure_simulation():
        """Simulate DNS resolution failure."""
        import requests
        raise requests.exceptions.ConnectionError("Failed to resolve hostname")


# Pre-configured test scenarios
TEST_SCENARIOS = {
    'normal_search': {
        'unsplash_response': MockUnsplashAPI.successful_search_response(),
        'openai_description': MockOpenAIAPI.successful_description_response(),
        'openai_extraction': MockOpenAIAPI.successful_extraction_response(),
        'image_data': MockImageData.valid_png_bytes()
    },
    'empty_search': {
        'unsplash_response': MockUnsplashAPI.empty_search_response(),
        'openai_description': None,
        'openai_extraction': None,
        'image_data': None
    },
    'rate_limited': {
        'unsplash_response': MockUnsplashAPI.rate_limited_error(),
        'openai_description': MockOpenAIAPI.rate_limited_error(),
        'openai_extraction': MockOpenAIAPI.rate_limited_error(),
        'image_data': None
    },
    'large_dataset': {
        'unsplash_response': MockUnsplashAPI.large_result_set(total=50000),
        'openai_description': MockOpenAIAPI.successful_description_response(),
        'openai_extraction': MockOpenAIAPI.successful_extraction_response(),
        'image_data': MockImageData.valid_png_bytes()
    },
    'network_issues': {
        'unsplash_response': None,  # Will raise exception
        'openai_description': None,
        'openai_extraction': None,
        'image_data': MockImageData.corrupted_image_bytes()
    }
}