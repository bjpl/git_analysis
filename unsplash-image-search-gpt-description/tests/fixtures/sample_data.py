"""
Sample data and fixtures for testing the Unsplash Image Search application.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


# Sample Unsplash API responses
SAMPLE_UNSPLASH_SEARCH_RESPONSE = {
    "results": [
        {
            "id": "test_image_1",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:00:00Z",
            "width": 4000,
            "height": 3000,
            "color": "#5CB3CC",
            "blur_hash": "LJBWZnWB2yk8mQfQfQfQfQfQfQfQ",
            "description": "A beautiful mountain landscape",
            "alt_description": "Snow-capped mountains reflected in a crystal-clear lake",
            "urls": {
                "raw": "https://images.unsplash.com/photo-test1?ixid=test1",
                "full": "https://images.unsplash.com/photo-test1?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=test1.jpg&w=3600",
                "regular": "https://images.unsplash.com/photo-test1?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&dl=test1.jpg&w=1080",
                "small": "https://images.unsplash.com/photo-test1?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&dl=test1.jpg&w=400",
                "thumb": "https://images.unsplash.com/photo-test1?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&dl=test1.jpg&w=200"
            },
            "links": {
                "self": "https://api.unsplash.com/photos/test_image_1",
                "html": "https://unsplash.com/photos/test_image_1",
                "download": "https://unsplash.com/photos/test_image_1/download"
            },
            "user": {
                "id": "test_photographer_1",
                "username": "nature_photographer",
                "name": "Nature Photographer",
                "portfolio_url": "https://example.com/portfolio",
                "bio": "Professional landscape photographer",
                "location": "Colorado, USA",
                "total_likes": 1000,
                "total_photos": 200,
                "total_collections": 10
            },
            "tags": [
                {"title": "mountain"}, {"title": "landscape"}, {"title": "nature"}
            ],
            "likes": 150,
            "downloads": 5000
        },
        {
            "id": "test_image_2",
            "created_at": "2023-01-02T12:00:00Z",
            "updated_at": "2023-01-02T12:00:00Z",
            "width": 3000,
            "height": 4000,
            "color": "#1A1A1A",
            "blur_hash": "L02EpRxu9FRj~qfQfQfQfQfQfQfQ",
            "description": "Urban nightscape",
            "alt_description": "City skyline at night with bright lights",
            "urls": {
                "raw": "https://images.unsplash.com/photo-test2?ixid=test2",
                "full": "https://images.unsplash.com/photo-test2?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=test2.jpg&w=3600",
                "regular": "https://images.unsplash.com/photo-test2?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&dl=test2.jpg&w=1080",
                "small": "https://images.unsplash.com/photo-test2?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&dl=test2.jpg&w=400",
                "thumb": "https://images.unsplash.com/photo-test2?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=srgb&dl=test2.jpg&w=200"
            },
            "links": {
                "self": "https://api.unsplash.com/photos/test_image_2",
                "html": "https://unsplash.com/photos/test_image_2",
                "download": "https://unsplash.com/photos/test_image_2/download"
            },
            "user": {
                "id": "test_photographer_2",
                "username": "city_photographer",
                "name": "Urban Explorer",
                "portfolio_url": "https://example.com/urban",
                "bio": "Street and architecture photographer",
                "location": "New York, USA",
                "total_likes": 2000,
                "total_photos": 500,
                "total_collections": 25
            },
            "tags": [
                {"title": "city"}, {"title": "night"}, {"title": "urban"}
            ],
            "likes": 300,
            "downloads": 8000
        }
    ],
    "total": 10000,
    "total_pages": 1000
}

# Sample OpenAI API responses
SAMPLE_OPENAI_DESCRIPTION_RESPONSES = {
    "mountain_landscape": {
        "choices": [{
            "message": {
                "content": """Esta imagen muestra un paisaje montañoso espectacular con picos nevados que se alzan majestuosamente hacia un cielo azul claro. En el primer plano, un lago de aguas cristalinas refleja perfectamente las montañas, creando una simetría visual impresionante. La vegetación alpina rodea el lago con tonos verdes vibrantes que contrastan beautifully con el blanco puro de la nieve en las cumbres. La composición transmite una sensación de tranquilidad y grandeza natural, característica de los paisajes de alta montaña."""
            }
        }],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 120,
            "total_tokens": 270
        }
    },
    "city_night": {
        "choices": [{
            "message": {
                "content": """Esta imagen captura la vibrante vida nocturna de una metrópolis moderna. Los rascacielos se elevan hacia el cielo oscuro, sus ventanas iluminadas creando un mosaico de luces doradas y blancas. Las calles están llenas de tráfico, con las luces de los vehículos formando ríos de color rojo y blanco que serpentean entre los edificios. La arquitectura moderna se combina con elementos urbanos clásicos, mientras que los letreros luminosos añaden toques de color neón al paisaje nocturno. La atmósfera es dinámica y llena de energía, representando el pulso constante de la vida urbana."""
            }
        }],
        "usage": {
            "prompt_tokens": 140,
            "completion_tokens": 130,
            "total_tokens": 270
        }
    }
}

SAMPLE_OPENAI_EXTRACTION_RESPONSES = {
    "mountain_landscape": {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "Sustantivos": [
                        "el paisaje", "las montañas", "los picos", "el lago", 
                        "las aguas", "la vegetación", "las cumbres", "el cielo"
                    ],
                    "Verbos": [
                        "muestra", "alzan", "refleja", "rodea", "contrastan", "transmite"
                    ],
                    "Adjetivos": [
                        "espectacular", "nevados", "majestuosamente", "cristalinas", 
                        "visual", "vibrantes", "puro", "natural"
                    ],
                    "Adverbios": [
                        "perfectamente", "beautifully"
                    ],
                    "Frases clave": [
                        "paisaje montañoso", "picos nevados", "aguas cristalinas",
                        "vegetación alpina", "alta montaña"
                    ]
                })
            }
        }]
    },
    "city_night": {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "Sustantivos": [
                        "la vida", "la metrópolis", "los rascacielos", "las ventanas",
                        "las calles", "el tráfico", "los vehículos", "los edificios"
                    ],
                    "Verbos": [
                        "captura", "elevan", "creando", "serpentean", "combina", "añaden"
                    ],
                    "Adjetivos": [
                        "vibrante", "nocturna", "moderna", "iluminadas", "doradas",
                        "urbanos", "luminosos", "dinámica"
                    ],
                    "Adverbios": [
                        "perfectamente", "constantemente"
                    ],
                    "Frases clave": [
                        "vida nocturna", "metrópolis moderna", "paisaje nocturno",
                        "vida urbana", "arquitectura moderna"
                    ]
                })
            }
        }]
    }
}

SAMPLE_TRANSLATION_RESPONSES = {
    "paisaje montañoso": "mountain landscape",
    "picos nevados": "snowy peaks",
    "aguas cristalinas": "crystal clear waters",
    "vegetación alpina": "alpine vegetation",
    "alta montaña": "high mountain",
    "vida nocturna": "nightlife", 
    "metrópolis moderna": "modern metropolis",
    "paisaje nocturno": "night landscape",
    "vida urbana": "urban life",
    "arquitectura moderna": "modern architecture"
}

# Sample session data
SAMPLE_SESSION_DATA = {
    "sessions": [
        {
            "session_start": "2023-01-01T10:00:00",
            "session_end": "2023-01-01T10:45:00",
            "entries": [
                {
                    "timestamp": "2023-01-01T10:15:00",
                    "query": "mountain landscape",
                    "image_url": "https://images.unsplash.com/photo-test1",
                    "user_note": "Beautiful mountain scene for vocabulary practice",
                    "generated_description": "Esta imagen muestra un paisaje montañoso espectacular..."
                },
                {
                    "timestamp": "2023-01-01T10:30:00",
                    "query": "city night",
                    "image_url": "https://images.unsplash.com/photo-test2",
                    "user_note": "Urban nightscape",
                    "generated_description": "Esta imagen captura la vibrante vida nocturna..."
                }
            ],
            "vocabulary_learned": 10,
            "target_phrases": [
                "paisaje montañoso - mountain landscape",
                "picos nevados - snowy peaks",
                "aguas cristalinas - crystal clear waters",
                "vida nocturna - nightlife",
                "metrópolis moderna - modern metropolis"
            ]
        },
        {
            "session_start": "2023-01-02T14:00:00", 
            "session_end": "2023-01-02T14:30:00",
            "entries": [
                {
                    "timestamp": "2023-01-02T14:15:00",
                    "query": "ocean sunset",
                    "image_url": "https://images.unsplash.com/photo-test3",
                    "user_note": "Sunset over the ocean",
                    "generated_description": "Un hermoso atardecer sobre el océano..."
                }
            ],
            "vocabulary_learned": 5,
            "target_phrases": [
                "atardecer - sunset",
                "océano - ocean",
                "horizonte - horizon"
            ]
        }
    ]
}

# Sample vocabulary CSV data
SAMPLE_VOCABULARY_CSV_DATA = [
    ["Spanish", "English", "Date", "Search Query", "Image URL", "Context"],
    ["paisaje montañoso", "mountain landscape", "2023-01-01 10:15", "mountain landscape", "https://images.unsplash.com/photo-test1", "Esta imagen muestra un paisaje montañoso espectacular..."],
    ["picos nevados", "snowy peaks", "2023-01-01 10:16", "mountain landscape", "https://images.unsplash.com/photo-test1", "picos nevados que se alzan majestuosamente"],
    ["aguas cristalinas", "crystal clear waters", "2023-01-01 10:17", "mountain landscape", "https://images.unsplash.com/photo-test1", "un lago de aguas cristalinas refleja perfectamente"],
    ["vida nocturna", "nightlife", "2023-01-01 10:30", "city night", "https://images.unsplash.com/photo-test2", "captura la vibrante vida nocturna de una metrópolis"],
    ["arquitectura moderna", "modern architecture", "2023-01-01 10:31", "city night", "https://images.unsplash.com/photo-test2", "La arquitectura moderna se combina con elementos"]
]

# Error response samples
ERROR_RESPONSES = {
    "unsplash_rate_limit": {
        "status_code": 429,
        "json": {"errors": ["Rate Limit Exceeded"]},
        "headers": {"X-Ratelimit-Remaining": "0", "X-Ratelimit-Limit": "50"}
    },
    "unsplash_invalid_key": {
        "status_code": 401,
        "json": {"errors": ["OAuth error: The access token is invalid"]}
    },
    "openai_rate_limit": {
        "error": {
            "message": "Rate limit reached for requests",
            "type": "insufficient_quota",
            "param": None,
            "code": "rate_limit_exceeded"
        }
    },
    "openai_invalid_key": {
        "error": {
            "message": "Invalid API key provided",
            "type": "invalid_request_error",
            "param": None,
            "code": "invalid_api_key"
        }
    }
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "api_call_timeout": 10.0,  # seconds
    "image_download_timeout": 15.0,  # seconds
    "description_generation_timeout": 30.0,  # seconds
    "phrase_extraction_timeout": 20.0,  # seconds
    "translation_timeout": 10.0,  # seconds
    "file_save_timeout": 2.0,  # seconds
    "ui_response_time": 0.5,  # seconds
    "memory_usage_mb": 200,  # MB
    "cache_size_limit": 50  # items
}

# Test image data (1x1 pixel images in different formats)
TEST_IMAGE_DATA = {
    "png_1x1": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82',
    "jpg_1x1": b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
}

# Configuration test data
TEST_CONFIG_DATA = {
    "valid_config": {
        "API": {
            "unsplash_access_key": "test_unsplash_key_123",
            "openai_api_key": "sk-test_openai_key_123",
            "gpt_model": "gpt-4o-mini"
        },
        "Paths": {
            "data_dir": "test_data",
            "log_file": "test_data/session_log.json",
            "vocabulary_file": "test_data/vocabulary.csv"
        },
        "UI": {
            "window_width": "1100",
            "window_height": "800",
            "font_size": "12"
        }
    },
    "invalid_config_missing_keys": {
        "API": {
            "unsplash_access_key": "",
            "openai_api_key": "",
            "gpt_model": "gpt-4o-mini"
        }
    }
}

# Edge cases for testing
EDGE_CASES = {
    "empty_search_query": "",
    "very_long_query": "a" * 1000,
    "special_characters_query": "café niño montaña corazón",
    "unicode_query": "🏔️🌊🌅🏙️",
    "empty_description": "",
    "very_long_description": "Esta es una descripción muy larga. " * 100,
    "malformed_json_extraction": '{"Sustantivos": ["el paisaje", "las montañas",], "Verbos": [}',
    "empty_translation": "",
    "very_long_phrase": "una frase extremadamente larga que podría causar problemas en el sistema de traducción y manejo de datos",
    "special_characters_phrase": "niño con corazón en montaña",
    "unicode_phrase": "emoji 🏔️ en frase",
    "duplicate_vocabulary": "paisaje montañoso",
    "corrupted_image_data": b"not_an_image_file_content",
    "large_image_url": "https://images.unsplash.com/" + "x" * 2000
}


def create_sample_files(test_dir: Path):
    """Create sample test files in the test directory."""
    # Create sample session log
    session_file = test_dir / "session_log.json"
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_SESSION_DATA, f, ensure_ascii=False, indent=2)
    
    # Create sample vocabulary CSV
    vocab_file = test_dir / "vocabulary.csv"
    import csv
    with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in SAMPLE_VOCABULARY_CSV_DATA:
            writer.writerow(row)
    
    # Create sample config file
    config_file = test_dir / "config.ini"
    import configparser
    config = configparser.ConfigParser()
    config.read_dict(TEST_CONFIG_DATA["valid_config"])
    with open(config_file, 'w') as f:
        config.write(f)
    
    return {
        "session_file": session_file,
        "vocab_file": vocab_file,
        "config_file": config_file
    }


def get_test_scenario(scenario_name: str):
    """Get a specific test scenario by name."""
    scenarios = {
        "successful_search": {
            "query": "mountain landscape",
            "expected_results": 2,
            "expected_phrases": ["paisaje montañoso", "picos nevados", "aguas cristalinas"]
        },
        "no_results_search": {
            "query": "nonexistentterm123xyz",
            "expected_results": 0,
            "expected_phrases": []
        },
        "rate_limited_search": {
            "query": "popular query",
            "response": ERROR_RESPONSES["unsplash_rate_limit"],
            "expected_error": "Rate Limit Exceeded"
        },
        "invalid_api_key": {
            "query": "any query",
            "response": ERROR_RESPONSES["unsplash_invalid_key"],
            "expected_error": "Invalid API key"
        }
    }
    return scenarios.get(scenario_name)


# Helper functions for test data creation
def generate_mock_response(response_type: str, **kwargs):
    """Generate mock responses for different APIs."""
    if response_type == "unsplash_search":
        return SAMPLE_UNSPLASH_SEARCH_RESPONSE
    elif response_type == "openai_description":
        query = kwargs.get("query", "mountain_landscape")
        return SAMPLE_OPENAI_DESCRIPTION_RESPONSES.get(query, SAMPLE_OPENAI_DESCRIPTION_RESPONSES["mountain_landscape"])
    elif response_type == "openai_extraction":
        query = kwargs.get("query", "mountain_landscape")  
        return SAMPLE_OPENAI_EXTRACTION_RESPONSES.get(query, SAMPLE_OPENAI_EXTRACTION_RESPONSES["mountain_landscape"])
    elif response_type == "openai_translation":
        phrase = kwargs.get("phrase", "paisaje montañoso")
        translation = SAMPLE_TRANSLATION_RESPONSES.get(phrase, "translated phrase")
        return {"choices": [{"message": {"content": translation}}]}
    else:
        raise ValueError(f"Unknown response type: {response_type}")


if __name__ == "__main__":
    # If run as script, create sample files for manual testing
    test_dir = Path("sample_test_data")
    test_dir.mkdir(exist_ok=True)
    files = create_sample_files(test_dir)
    print(f"Sample test files created in {test_dir}:")
    for name, path in files.items():
        print(f"  {name}: {path}")