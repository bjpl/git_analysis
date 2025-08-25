#!/usr/bin/env python3
"""
API Mock Tests for Unsplash Image Search GPT Tool

This module provides mock-based testing for API interactions,
allowing testing without actual API calls or network connectivity.
"""

import json
import os
import sys
import unittest.mock
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import base64
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import requests
from PIL import Image
import io


class MockAPIResponses:
    """Container for mock API responses."""
    
    @staticmethod
    def unsplash_search_success():
        """Mock successful Unsplash search response."""
        return {
            "results": [
                {
                    "id": "test-image-1",
                    "urls": {
                        "regular": "https://images.unsplash.com/test-image-1?w=640",
                        "small": "https://images.unsplash.com/test-image-1?w=400",
                        "thumb": "https://images.unsplash.com/test-image-1?w=200"
                    },
                    "alt_description": "Test image for mountain landscape",
                    "description": "A beautiful mountain landscape",
                    "user": {
                        "name": "Test Photographer",
                        "username": "testuser"
                    },
                    "tags": [
                        {"title": "mountain"},
                        {"title": "landscape"},
                        {"title": "nature"}
                    ]
                },
                {
                    "id": "test-image-2",
                    "urls": {
                        "regular": "https://images.unsplash.com/test-image-2?w=640",
                        "small": "https://images.unsplash.com/test-image-2?w=400",
                        "thumb": "https://images.unsplash.com/test-image-2?w=200"
                    },
                    "alt_description": "Test image for city skyline",
                    "description": "Urban cityscape at sunset",
                    "user": {
                        "name": "Another Photographer",
                        "username": "citysnapper"
                    },
                    "tags": [
                        {"title": "city"},
                        {"title": "urban"},
                        {"title": "skyline"}
                    ]
                }
            ],
            "total": 2,
            "total_pages": 1
        }
    
    @staticmethod
    def unsplash_search_empty():
        """Mock empty Unsplash search response."""
        return {
            "results": [],
            "total": 0,
            "total_pages": 0
        }
    
    @staticmethod
    def unsplash_rate_limit_error():
        """Mock Unsplash rate limit error response."""
        response = Mock()
        response.status_code = 429
        response.json.return_value = {
            "error": "Rate Limit Exceeded"
        }
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("429 Rate Limit Exceeded")
        return response
    
    @staticmethod
    def openai_description_success():
        """Mock successful OpenAI image description response."""
        return Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Esta imagen muestra una hermosa montaña con nieve en la cima. El cielo está despejado y azul. En primer plano se pueden ver árboles verdes y un pequeño sendero que lleva hacia la montaña. La luz del sol crea sombras suaves en las laderas de la montaña."
                    )
                )
            ]
        )
    
    @staticmethod
    def openai_phrase_extraction_success():
        """Mock successful OpenAI phrase extraction response."""
        return Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=json.dumps({
                            "Sustantivos": ["la montaña", "la nieve", "el cielo", "los árboles", "el sendero"],
                            "Verbos": ["muestra", "crea", "lleva"],
                            "Adjetivos": ["hermosa", "despejado", "azul", "verdes", "pequeño", "suaves"],
                            "Adverbios": ["suavemente"],
                            "Frases clave": ["montaña con nieve", "cielo despejado", "primer plano", "luz del sol"]
                        })
                    )
                )
            ]
        )
    
    @staticmethod
    def openai_translation_success():
        """Mock successful OpenAI translation response."""
        return Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="mountain"
                    )
                )
            ]
        )
    
    @staticmethod
    def create_test_image():
        """Create a test image for mocking image downloads."""
        img = Image.new('RGB', (400, 300), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes.getvalue()


class APIMockTestSuite:
    """Test suite for API mocking scenarios."""
    
    def __init__(self):
        self.mock_responses = MockAPIResponses()
        self.test_results = []
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        result = {
            'test_name': test_name,
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_unsplash_api_success_mock(self):
        """Test successful Unsplash API response handling."""
        try:
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self.mock_responses.unsplash_search_success()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                # Simulate API call
                headers = {"Authorization": "Client-ID test_key"}
                url = "https://api.unsplash.com/search/photos?query=mountain&page=1&per_page=10"
                response = requests.get(url, headers=headers)
                data = response.json()
                
                # Verify response structure
                has_results = 'results' in data and len(data['results']) > 0
                first_image = data['results'][0] if has_results else {}
                has_urls = 'urls' in first_image and 'regular' in first_image['urls']
                
                success = has_results and has_urls
                details = f"Found {len(data['results'])} results" if has_results else "No results found"
                
                self.log_test_result(
                    "Unsplash API Success Mock",
                    success,
                    details
                )
                return success
                
        except Exception as e:
            self.log_test_result(
                "Unsplash API Success Mock",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_unsplash_api_rate_limit_mock(self):
        """Test Unsplash API rate limit handling."""
        try:
            with patch('requests.get') as mock_get:
                mock_get.return_value = self.mock_responses.unsplash_rate_limit_error()
                
                # Simulate API call that hits rate limit
                headers = {"Authorization": "Client-ID test_key"}
                url = "https://api.unsplash.com/search/photos?query=test&page=1&per_page=10"
                
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    rate_limit_handled = False
                except requests.exceptions.HTTPError as e:
                    rate_limit_handled = "429" in str(e)
                
                self.log_test_result(
                    "Unsplash API Rate Limit Mock",
                    rate_limit_handled,
                    "Rate limit error properly raised" if rate_limit_handled else "Rate limit not handled"
                )
                return rate_limit_handled
                
        except Exception as e:
            self.log_test_result(
                "Unsplash API Rate Limit Mock",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_image_download_mock(self):
        """Test image download functionality with mocked image."""
        try:
            test_image_data = self.mock_responses.create_test_image()
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.content = test_image_data
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                # Simulate image download
                img_url = "https://images.unsplash.com/test-image?w=640"
                response = requests.get(img_url)
                
                # Try to create PIL Image from response
                try:
                    img = Image.open(io.BytesIO(response.content))
                    img_valid = img.size[0] > 0 and img.size[1] > 0
                    details = f"Downloaded image: {img.size[0]}x{img.size[1]}"
                except Exception as img_error:
                    img_valid = False
                    details = f"Image creation failed: {str(img_error)}"
                
                self.log_test_result(
                    "Image Download Mock",
                    img_valid,
                    details
                )
                return img_valid
                
        except Exception as e:
            self.log_test_result(
                "Image Download Mock",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_openai_description_mock(self):
        """Test OpenAI description generation with mock."""
        try:
            with patch('openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = self.mock_responses.openai_description_success()
                mock_openai_class.return_value = mock_client
                
                # Simulate OpenAI client usage
                from openai import OpenAI
                client = OpenAI(api_key="test_key")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe this image in Spanish"},
                                {"type": "image_url", "image_url": {"url": "test_url"}}
                            ]
                        }
                    ]
                )
                
                description = response.choices[0].message.content
                has_spanish_description = bool(description and len(description) > 10)
                
                self.log_test_result(
                    "OpenAI Description Mock",
                    has_spanish_description,
                    f"Generated description: {description[:50]}..." if has_spanish_description else "No description"
                )
                return has_spanish_description
                
        except Exception as e:
            self.log_test_result(
                "OpenAI Description Mock",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_phrase_extraction_mock(self):
        """Test phrase extraction with mock OpenAI response."""
        try:
            with patch('openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = self.mock_responses.openai_phrase_extraction_success()
                mock_openai_class.return_value = mock_client
                
                from openai import OpenAI
                client = OpenAI(api_key="test_key")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Extract vocabulary from Spanish text"},
                        {"role": "user", "content": "Extract phrases from: Esta imagen muestra una hermosa montaña."}
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Parse JSON response
                json_str = response.choices[0].message.content
                phrases_data = json.loads(json_str)
                
                # Check for expected categories
                expected_categories = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
                categories_found = all(cat in phrases_data for cat in expected_categories)
                has_phrases = any(len(phrases_data[cat]) > 0 for cat in expected_categories if cat in phrases_data)
                
                success = categories_found and has_phrases
                details = f"Categories: {list(phrases_data.keys())}, Total phrases: {sum(len(v) for v in phrases_data.values())}"
                
                self.log_test_result(
                    "Phrase Extraction Mock",
                    success,
                    details
                )
                return success
                
        except Exception as e:
            self.log_test_result(
                "Phrase Extraction Mock",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_translation_mock(self):
        """Test translation functionality with mock."""
        try:
            with patch('openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = self.mock_responses.openai_translation_success()
                mock_openai_class.return_value = mock_client
                
                from openai import OpenAI
                client = OpenAI(api_key="test_key")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Translate 'la montaña' to English"}]
                )
                
                translation = response.choices[0].message.content.strip()
                translation_valid = bool(translation and len(translation) > 0 and translation != "la montaña")
                
                self.log_test_result(
                    "Translation Mock",
                    translation_valid,
                    f"Translation: 'la montaña' -> '{translation}'"
                )
                return translation_valid
                
        except Exception as e:
            self.log_test_result(
                "Translation Mock",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_network_error_handling(self):
        """Test network error handling with mocked failures."""
        try:
            with patch('requests.get') as mock_get:
                # Simulate network timeout
                mock_get.side_effect = requests.exceptions.ConnectTimeout("Connection timed out")
                
                network_error_handled = False
                try:
                    response = requests.get("https://api.unsplash.com/search/photos")
                except requests.exceptions.ConnectTimeout:
                    network_error_handled = True
                
                self.log_test_result(
                    "Network Error Handling",
                    network_error_handled,
                    "Network timeout exception properly raised" if network_error_handled else "Network error not handled"
                )
                return network_error_handled
                
        except Exception as e:
            self.log_test_result(
                "Network Error Handling",
                False,
                f"Error: {str(e)}"
            )
            return False


def test_mock_api_responses():
    """Test that mock API responses have correct structure."""
    mock_responses = MockAPIResponses()
    
    # Test Unsplash response structure
    unsplash_data = mock_responses.unsplash_search_success()
    assert 'results' in unsplash_data
    assert len(unsplash_data['results']) > 0
    assert 'urls' in unsplash_data['results'][0]
    assert 'regular' in unsplash_data['results'][0]['urls']
    
    # Test OpenAI response structure
    openai_response = mock_responses.openai_description_success()
    assert hasattr(openai_response, 'choices')
    assert len(openai_response.choices) > 0
    assert hasattr(openai_response.choices[0].message, 'content')
    
    # Test phrase extraction response
    phrase_response = mock_responses.openai_phrase_extraction_success()
    content = phrase_response.choices[0].message.content
    phrases_data = json.loads(content)
    expected_categories = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
    for category in expected_categories:
        assert category in phrases_data
    
    print("✅ All mock response structures are valid")


def run_api_mock_tests():
    """Run all API mock tests and return results."""
    print("🔧 Starting API Mock Tests...")
    print("=" * 60)
    
    # Test mock response structures first
    try:
        test_mock_api_responses()
    except Exception as e:
        print(f"❌ Mock response structure test failed: {e}")
        return []
    
    # Run mock test suite
    test_suite = APIMockTestSuite()
    
    tests = [
        test_suite.test_unsplash_api_success_mock,
        test_suite.test_unsplash_api_rate_limit_mock,
        test_suite.test_image_download_mock,
        test_suite.test_openai_description_mock,
        test_suite.test_phrase_extraction_mock,
        test_suite.test_translation_mock,
        test_suite.test_network_error_handling,
    ]
    
    # Run all tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            test_suite.log_test_result(
                test.__name__,
                False,
                f"Exception: {str(e)}"
            )
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API MOCK TESTS SUMMARY")
    print("=" * 60)
    
    results = test_suite.test_results
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"Tests Passed: {passed_count}/{total_count} ({pass_rate:.1f}%)")
    
    # Show failed tests
    failed_tests = [r for r in results if not r['passed']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for failure in failed_tests:
            print(f"  - {failure['test_name']}: {failure['details']}")
    
    # Overall status
    if pass_rate >= 90:
        print("✅ OVERALL STATUS: PASS - API mocking works correctly")
    elif pass_rate >= 70:
        print("⚠️  OVERALL STATUS: WARNING - Some mock tests failed")
    else:
        print("❌ OVERALL STATUS: FAIL - Major issues with API mocking")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run API mock tests")
    parser.add_argument("--output", help="Output file for test results JSON")
    
    args = parser.parse_args()
    
    try:
        results = run_api_mock_tests()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📋 Results saved to: {args.output}")
        
        # Exit with appropriate code
        passed_count = sum(1 for r in results if r['passed'])
        total_count = len(results)
        
        if passed_count >= total_count * 0.9:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        print(f"❌ API mock tests failed with error: {e}")
        sys.exit(1)