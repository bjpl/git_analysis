"""
Unit tests for OpenAI API service functionality.
Tests the ImageSearchApp's OpenAI integration methods.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_OPENAI_DESCRIPTION_RESPONSES,
    SAMPLE_OPENAI_EXTRACTION_RESPONSES,
    SAMPLE_TRANSLATION_RESPONSES,
    ERROR_RESPONSES,
    EDGE_CASES,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.unit
class TestOpenAIService:
    """Test suite for OpenAI API service functionality."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    @pytest.fixture
    def mock_openai_description_success(self):
        """Mock successful OpenAI description generation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = SAMPLE_OPENAI_DESCRIPTION_RESPONSES["mountain_landscape"]["choices"][0]["message"]["content"]
        return mock_response

    @pytest.fixture
    def mock_openai_extraction_success(self):
        """Mock successful OpenAI phrase extraction."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = SAMPLE_OPENAI_EXTRACTION_RESPONSES["mountain_landscape"]["choices"][0]["message"]["content"]
        return mock_response

    def test_generate_description_success(self, app_instance, mock_openai_client, mock_openai_description_success):
        """Test successful image description generation."""
        # Setup mocks
        mock_openai_client.chat.completions.create.return_value = mock_openai_description_success
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://images.unsplash.com/test-image"
        
        # Setup app state
        app_instance.search_entry = Mock()
        app_instance.search_entry.get.return_value = "mountain landscape"
        app_instance.note_text = Mock()
        app_instance.note_text.get.return_value = "Beautiful mountain scene"
        app_instance.image_label = Mock()
        app_instance.image_label.image = Mock()  # Simulate image is loaded

        # Test the method
        query = "mountain landscape"
        user_note = "Beautiful mountain scene"
        
        # Call the thread method directly to avoid threading complications
        app_instance.thread_generate_description(query, user_note)

        # Verify OpenAI API was called correctly
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args
        
        # Check the call arguments
        assert call_args[1]["model"] == "gpt-4o-mini"
        assert len(call_args[1]["messages"]) == 1
        assert call_args[1]["messages"][0]["role"] == "user"
        assert "content" in call_args[1]["messages"][0]
        
        # Check that both text and image_url are in content
        content = call_args[1]["messages"][0]["content"]
        assert len(content) == 2  # text and image_url
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"
        assert "Analiza la imagen" in content[0]["text"]
        assert user_note in content[0]["text"]

    def test_generate_description_no_image_url(self, app_instance, mock_openai_client):
        """Test description generation when no image URL is available."""
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = None

        query = "mountain"
        user_note = ""
        
        # This should handle the error gracefully
        app_instance.thread_generate_description(query, user_note)
        
        # OpenAI should not be called
        mock_openai_client.chat.completions.create.assert_not_called()

    def test_generate_description_api_error(self, app_instance, mock_openai_client):
        """Test handling of OpenAI API errors."""
        # Setup mock to raise API error
        mock_openai_client.chat.completions.create.side_effect = Exception("API key invalid")
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://test.com/image"

        query = "mountain"
        user_note = ""
        
        # Should handle the error gracefully without raising
        app_instance.thread_generate_description(query, user_note)
        
        # Verify API was called (and failed)
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_generate_description_rate_limit_error(self, app_instance, mock_openai_client):
        """Test handling of OpenAI rate limit errors."""
        mock_openai_client.chat.completions.create.side_effect = Exception("rate_limit exceeded")
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://test.com/image"

        query = "mountain"
        user_note = ""
        
        app_instance.thread_generate_description(query, user_note)
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_generate_description_invalid_api_key(self, app_instance, mock_openai_client):
        """Test handling of invalid API key error."""
        mock_openai_client.chat.completions.create.side_effect = Exception("api_key invalid")
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://test.com/image"

        query = "mountain"
        user_note = ""
        
        app_instance.thread_generate_description(query, user_note)
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_generate_description_quota_exceeded(self, app_instance, mock_openai_client):
        """Test handling of quota exceeded error."""
        mock_openai_client.chat.completions.create.side_effect = Exception("insufficient_quota")
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://test.com/image"

        query = "mountain"
        user_note = ""
        
        app_instance.thread_generate_description(query, user_note)
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_extract_phrases_from_description_success(self, app_instance, mock_openai_client, mock_openai_extraction_success):
        """Test successful phrase extraction from description."""
        mock_openai_client.chat.completions.create.return_value = mock_openai_extraction_success
        app_instance.openai_client = mock_openai_client

        description = "Esta imagen muestra un paisaje montañoso espectacular..."
        
        # Call the method directly
        app_instance.extract_phrases_from_description(description)

        # Verify OpenAI API was called
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args

        # Check API call parameters
        assert call_args[1]["model"] == "gpt-4o-mini"
        assert call_args[1]["response_format"]["type"] == "json_object"
        assert len(call_args[1]["messages"]) == 2
        assert call_args[1]["messages"][0]["role"] == "system"
        assert call_args[1]["messages"][1]["role"] == "user"
        assert description in call_args[1]["messages"][1]["content"]

    def test_extract_phrases_json_decode_error(self, app_instance, mock_openai_client):
        """Test handling of malformed JSON from phrase extraction."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = EDGE_CASES["malformed_json_extraction"]
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        description = "Test description"
        
        # Should handle JSON error gracefully
        app_instance.extract_phrases_from_description(description)
        
        # Verify API was called
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_extract_phrases_empty_response(self, app_instance, mock_openai_client):
        """Test handling of empty extraction response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "{}"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        description = "Simple description"
        app_instance.extract_phrases_from_description(description)
        
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_translate_word_success(self, app_instance, mock_openai_client):
        """Test successful word translation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "mountain landscape"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("paisaje montañoso")
        
        assert result == "mountain landscape"
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_translate_word_with_context(self, app_instance, mock_openai_client):
        """Test word translation with context."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "snowy peaks"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        context = "Los picos nevados se reflejan en el lago"
        result = app_instance.translate_word("picos nevados", context)
        
        assert result == "snowy peaks"
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert context in prompt

    def test_translate_word_api_error(self, app_instance, mock_openai_client):
        """Test translation when API call fails."""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("test word")
        
        assert result == ""  # Should return empty string on error

    def test_translate_word_empty_phrase(self, app_instance, mock_openai_client):
        """Test translation with empty phrase."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = ""
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("")
        
        assert result == ""

    def test_translate_word_special_characters(self, app_instance, mock_openai_client):
        """Test translation with special characters."""
        mock_response = Mock()
        mock_response.choices = [Mock()]  
        mock_response.choices[0].message.content = "child with heart"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("niño con corazón")
        
        assert result == "child with heart"

    def test_display_extracted_phrases_empty(self, app_instance):
        """Test display of empty phrase groups."""
        # Setup mock GUI elements
        app_instance.extracted_inner_frame = Mock()
        app_instance.extracted_inner_frame.winfo_children.return_value = []

        # Test with empty groups
        app_instance.display_extracted_phrases({})
        
        # Should handle empty groups gracefully
        app_instance.extracted_inner_frame.winfo_children.assert_called_once()

    def test_display_extracted_phrases_with_data(self, app_instance):
        """Test display of phrase groups with data."""
        app_instance.extracted_inner_frame = Mock()
        app_instance.extracted_inner_frame.winfo_children.return_value = []

        test_groups = {
            "Sustantivos": ["el paisaje", "las montañas"],
            "Verbos": ["muestra", "refleja"],
            "Adjetivos": ["hermoso", "cristalino"]
        }

        app_instance.display_extracted_phrases(test_groups)
        
        # Verify groups were stored
        assert app_instance.extracted_phrases == test_groups

    def test_sort_ignoring_articles(self, app_instance):
        """Test sorting phrases while ignoring Spanish articles."""
        phrases = ["las montañas", "el paisaje", "la casa", "los árboles"]
        
        # Create a simple sort function based on app logic
        def sort_ignoring_articles(phrase):
            words = phrase.lower().split()
            if words and words[0] in ["el", "la", "los", "las"]:
                return " ".join(words[1:])
            return phrase.lower()

        sorted_phrases = sorted(phrases, key=sort_ignoring_articles)
        
        # Should sort by the noun, not the article
        expected = ["los árboles", "la casa", "las montañas", "el paisaje"]
        assert sorted_phrases == expected

    @pytest.mark.slow
    def test_description_generation_performance(self, app_instance, mock_openai_client, mock_openai_description_success):
        """Test that description generation completes within time threshold."""
        import time
        
        mock_openai_client.chat.completions.create.return_value = mock_openai_description_success
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://test.com/image"

        start_time = time.time()
        app_instance.thread_generate_description("mountain", "")
        duration = time.time() - start_time

        assert duration < PERFORMANCE_BENCHMARKS["description_generation_timeout"]

    @pytest.mark.slow  
    def test_phrase_extraction_performance(self, app_instance, mock_openai_client, mock_openai_extraction_success):
        """Test that phrase extraction completes within time threshold."""
        import time
        
        mock_openai_client.chat.completions.create.return_value = mock_openai_extraction_success
        app_instance.openai_client = mock_openai_client

        start_time = time.time()
        app_instance.extract_phrases_from_description("Test description")
        duration = time.time() - start_time

        assert duration < PERFORMANCE_BENCHMARKS["phrase_extraction_timeout"]

    def test_api_call_retry_with_gpt_calls(self, app_instance, mock_openai_client):
        """Test retry mechanism specifically with OpenAI calls."""
        # Mock function that fails then succeeds
        mock_create = Mock()
        mock_create.side_effect = [Exception("Temporary error"), Mock()]
        mock_openai_client.chat.completions.create = mock_create
        app_instance.openai_client = mock_openai_client

        def mock_gpt_call():
            return app_instance.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}]
            )

        with patch('time.sleep'):  # Speed up test
            result = app_instance.api_call_with_retry(mock_gpt_call, max_retries=3)

        assert result is not None
        assert mock_create.call_count == 2

    def test_long_description_handling(self, app_instance, mock_openai_client):
        """Test handling of very long descriptions."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = EDGE_CASES["very_long_description"]
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        # Should handle long description without issues
        app_instance.extract_phrases_from_description(EDGE_CASES["very_long_description"])
        
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_unicode_phrase_translation(self, app_instance, mock_openai_client):
        """Test translation of phrases containing Unicode characters."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "emoji mountain in phrase"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word(EDGE_CASES["unicode_phrase"])
        
        assert result == "emoji mountain in phrase"

    def test_description_with_user_context(self, app_instance, mock_openai_client, mock_openai_description_success):
        """Test description generation including user context."""
        mock_openai_client.chat.completions.create.return_value = mock_openai_description_success
        app_instance.openai_client = mock_openai_client
        app_instance.current_image_url = "https://test.com/image"

        query = "mountain"
        user_note = "This is a photo I took during my hiking trip"
        
        app_instance.thread_generate_description(query, user_note)

        call_args = mock_openai_client.chat.completions.create.call_args
        prompt_text = call_args[1]["messages"][0]["content"][0]["text"]
        
        # User note should be included in the prompt
        assert user_note in prompt_text

    def test_phrase_extraction_categories(self, app_instance, mock_openai_client):
        """Test that phrase extraction includes all expected categories."""
        # Mock response with all categories
        complete_response = {
            "Sustantivos": ["el paisaje", "las montañas"],
            "Verbos": ["muestra", "refleja"],
            "Adjetivos": ["hermoso", "cristalino"],
            "Adverbios": ["perfectamente"],
            "Frases clave": ["paisaje montañoso", "alta montaña"]
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(complete_response)
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        app_instance.extract_phrases_from_description("Test description")
        
        # Verify call included all category instructions
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        
        expected_categories = ["Sustantivos", "Verbos", "Adjetivos", "Adverbios", "Frases clave"]
        for category in expected_categories:
            assert category in prompt


@pytest.mark.integration
class TestOpenAIIntegration:
    """Integration tests for OpenAI service (require valid API key)."""

    @pytest.mark.api
    def test_real_openai_description_call(self, app_instance):
        """Test actual API call to OpenAI for description (requires valid API key)."""
        pytest.skip("Requires valid API key and network connection")
        
        # This test would make a real API call
        # Only enable if you have valid credentials
        # result = app_instance.thread_generate_description("mountain", "test")
        # assert len(result) > 0

    @pytest.mark.api
    def test_real_openai_extraction_call(self, app_instance):
        """Test actual API call to OpenAI for extraction (requires valid API key)."""
        pytest.skip("Requires valid API key and network connection")
        
        # This test would make a real API call
        # description = "Esta imagen muestra un hermoso paisaje montañoso."
        # app_instance.extract_phrases_from_description(description)
        # assert len(app_instance.extracted_phrases) > 0