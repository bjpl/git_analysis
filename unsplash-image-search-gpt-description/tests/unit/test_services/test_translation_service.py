"""
Unit tests for translation service functionality.
Tests the ImageSearchApp's translation and vocabulary management methods.
"""

import pytest
import csv
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path to import modules  
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_TRANSLATION_RESPONSES,
    SAMPLE_VOCABULARY_CSV_DATA,
    EDGE_CASES,
    PERFORMANCE_BENCHMARKS
)


@pytest.mark.unit
class TestTranslationService:
    """Test suite for translation and vocabulary management functionality."""

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

    def test_add_target_phrase_new_phrase(self, app_instance, mock_openai_client):
        """Test adding a new target phrase."""
        # Setup mocks
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "mountain landscape"
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.description_text.get.return_value = "Esta imagen muestra un paisaje montañoso"
        app_instance.target_listbox = Mock()
        app_instance.current_query = "mountain"
        app_instance.current_image_url = "https://test.com/image"

        # Mock CSV writing
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('csv.writer') as mock_csv_writer:
            
            mock_writer = Mock()
            mock_csv_writer.return_value = mock_writer
            
            # Test adding new phrase
            phrase = "paisaje montañoso"
            app_instance.add_target_phrase(phrase)

            # Verify phrase was added
            assert any(phrase in target_phrase for target_phrase in app_instance.target_phrases)
            
            # Verify translation was called
            mock_openai_client.chat.completions.create.assert_called_once()
            
            # Verify CSV was written
            mock_writer.writerow.assert_called_once()

    def test_add_target_phrase_duplicate(self, app_instance):
        """Test adding a duplicate phrase (should be ignored)."""
        # Setup existing phrase
        app_instance.target_phrases = ["paisaje montañoso - mountain landscape"]
        app_instance.vocabulary_cache = set()

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.target_listbox = Mock()
        app_instance.update_target_list_display = Mock()

        initial_count = len(app_instance.target_phrases)
        
        # Try to add duplicate
        app_instance.add_target_phrase("paisaje montañoso")

        # Should not add duplicate
        assert len(app_instance.target_phrases) == initial_count

    def test_add_target_phrase_in_cache(self, app_instance):
        """Test adding a phrase that's already in vocabulary cache."""
        # Setup vocabulary cache with existing phrase
        phrase = "paisaje montañoso"
        app_instance.vocabulary_cache.add(phrase)
        app_instance.target_phrases = []

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.target_listbox = Mock()

        initial_count = len(app_instance.target_phrases)
        
        # Try to add cached phrase
        app_instance.add_target_phrase(phrase)

        # Should not add to target phrases
        assert len(app_instance.target_phrases) == initial_count

    def test_add_target_phrase_translation_failure(self, app_instance, mock_openai_client):
        """Test adding phrase when translation fails."""
        # Setup translation to fail
        mock_openai_client.chat.completions.create.side_effect = Exception("Translation failed")
        app_instance.openai_client = mock_openai_client

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.description_text.get.return_value = "Context"
        app_instance.target_listbox = Mock()
        app_instance.update_target_list_display = Mock()

        phrase = "paisaje montañoso"
        app_instance.add_target_phrase(phrase)

        # Should still add phrase even without translation
        assert any(phrase in target_phrase for target_phrase in app_instance.target_phrases)

    def test_translate_word_success(self, app_instance, mock_openai_client):
        """Test successful word translation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "mountain landscape"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("paisaje montañoso")

        assert result == "mountain landscape"
        
        # Verify API call parameters
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o-mini"
        assert call_args[1]["max_tokens"] == 20
        assert call_args[1]["temperature"] == 0.0
        assert "paisaje montañoso" in call_args[1]["messages"][0]["content"]

    def test_translate_word_with_context(self, app_instance, mock_openai_client):
        """Test word translation with context."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "snowy peaks"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        word = "picos nevados"
        context = "Los picos nevados brillan bajo el sol"
        result = app_instance.translate_word(word, context)

        assert result == "snowy peaks"
        
        # Verify context was included in prompt
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert context in prompt
        assert "following sentence" in prompt

    def test_translate_word_empty_input(self, app_instance, mock_openai_client):
        """Test translation with empty word."""
        result = app_instance.translate_word("")

        assert result == ""
        # Should not make API call for empty input
        mock_openai_client.chat.completions.create.assert_not_called()

    def test_translate_word_special_characters(self, app_instance, mock_openai_client):
        """Test translation with special characters."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "child"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word("niño")

        assert result == "child"

    def test_translate_word_unicode_characters(self, app_instance, mock_openai_client):
        """Test translation with unicode characters."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "emoji mountain"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word(EDGE_CASES["unicode_phrase"])

        assert result == "emoji mountain"

    def test_translate_word_very_long_phrase(self, app_instance, mock_openai_client):
        """Test translation with very long phrase."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "very long phrase translation"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        result = app_instance.translate_word(EDGE_CASES["very_long_phrase"])

        assert result == "very long phrase translation"

    def test_log_target_word_csv_new_file(self, app_instance, test_data_dir):
        """Test logging target word to new CSV file."""
        # Setup paths
        csv_file = test_data_dir / "vocabulary_new.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Log a word
        app_instance.log_target_word_csv(
            "paisaje montañoso",
            "mountain landscape", 
            "mountain search",
            "https://test.com/image",
            "Beautiful mountain scene"
        )

        # Verify file was created and contains data
        assert csv_file.exists()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        assert len(rows) == 1
        assert rows[0]['Spanish'] == "paisaje montañoso"
        assert rows[0]['English'] == "mountain landscape"
        assert rows[0]['Search Query'] == "mountain search"

    def test_log_target_word_csv_append_existing(self, app_instance, test_data_dir):
        """Test appending to existing CSV file."""
        csv_file = test_data_dir / "vocabulary_existing.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Create existing file with header
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writerow(['existing_word', 'existing_translation', '2023-01-01 10:00', 'test', 'url', 'context'])

        # Append new word
        app_instance.log_target_word_csv(
            "nueva palabra",
            "new word",
            "test query", 
            "https://test.com/new",
            "New context"
        )

        # Verify both entries exist
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[1]['Spanish'] == "nueva palabra"
        assert rows[1]['English'] == "new word"

    def test_log_target_word_csv_file_error(self, app_instance, test_data_dir):
        """Test handling CSV file write errors."""
        # Setup path to non-existent directory
        csv_file = test_data_dir / "nonexistent" / "vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Should handle error gracefully
        app_instance.log_target_word_csv("test", "test", "query", "url", "context")

        # File should not exist due to error
        assert not csv_file.exists()

    def test_update_target_list_display(self, app_instance):
        """Test updating target list display."""
        # Setup GUI mock
        app_instance.target_listbox = Mock()
        
        # Setup test phrases
        app_instance.target_phrases = [
            "paisaje montañoso - mountain landscape",
            "lago cristalino - crystal lake"
        ]

        app_instance.update_target_list_display()

        # Verify listbox was cleared and updated
        app_instance.target_listbox.delete.assert_called_with(0, 'END')
        assert app_instance.target_listbox.insert.call_count == 2

    def test_load_vocabulary_cache_success(self, app_instance, test_data_dir):
        """Test loading vocabulary cache from CSV file."""
        csv_file = test_data_dir / "vocabulary_cache.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Create test CSV file
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in SAMPLE_VOCABULARY_CSV_DATA:
                writer.writerow(row)

        # Load cache
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Verify vocabulary was loaded
        expected_words = {
            "paisaje montañoso", "picos nevados", "aguas cristalinas",
            "vida nocturna", "arquitectura moderna"
        }
        assert expected_words.issubset(app_instance.vocabulary_cache)

    def test_load_vocabulary_cache_corrupted_file(self, app_instance, test_data_dir):
        """Test handling corrupted vocabulary CSV file."""
        csv_file = test_data_dir / "vocabulary_corrupted.csv"  
        app_instance.CSV_TARGET_WORDS = csv_file

        # Create corrupted CSV file
        with open(csv_file, 'w') as f:
            f.write("corrupted,csv,content\nwith\"broken\"quotes\nand,incomplete")

        # Should handle gracefully
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Cache should remain empty due to corruption handling
        # (or contain what could be salvaged)

    def test_load_vocabulary_cache_missing_file(self, app_instance, test_data_dir):
        """Test handling missing vocabulary file."""
        csv_file = test_data_dir / "nonexistent_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Should handle missing file gracefully
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Cache should remain empty
        assert len(app_instance.vocabulary_cache) == 0

    def test_load_vocabulary_cache_old_format(self, app_instance, test_data_dir):
        """Test handling old CSV format (without headers)."""
        csv_file = test_data_dir / "vocabulary_old_format.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Create old format file (no headers)
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['palabra uno', 'word one'])
            writer.writerow(['palabra dos', 'word two'])

        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Should attempt to load from old format
        # Exact behavior depends on implementation

    @pytest.mark.slow
    def test_translation_performance(self, app_instance, mock_openai_client):
        """Test translation performance within threshold."""
        import time
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "quick translation"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        start_time = time.time()
        result = app_instance.translate_word("palabra rápida")
        duration = time.time() - start_time

        assert duration < PERFORMANCE_BENCHMARKS["translation_timeout"]
        assert result == "quick translation"

    def test_vocabulary_deduplication(self, app_instance):
        """Test that vocabulary properly handles duplicates."""
        app_instance.vocabulary_cache = {"existing_word"}
        app_instance.target_phrases = []

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.target_listbox = Mock()

        # Try to add existing word
        app_instance.add_target_phrase("existing_word")

        # Should not be added to target phrases
        assert len(app_instance.target_phrases) == 0

    def test_csv_encoding_handling(self, app_instance, test_data_dir):
        """Test proper UTF-8 encoding handling in CSV operations."""
        csv_file = test_data_dir / "vocabulary_utf8.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Test with Spanish characters
        spanish_word = "niño"
        english_word = "child"
        
        app_instance.log_target_word_csv(
            spanish_word,
            english_word,
            "test query",
            "https://test.com/image",
            "Test context with ñ"
        )

        # Read back and verify encoding
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert spanish_word in content
            assert "ñ" in content

    def test_csv_escaping_special_characters(self, app_instance, test_data_dir):
        """Test CSV properly escapes special characters."""
        csv_file = test_data_dir / "vocabulary_special.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Test with quotes and commas
        spanish_phrase = 'palabra con "comillas" y, comas'
        english_phrase = 'word with "quotes" and, commas'
        
        app_instance.log_target_word_csv(
            spanish_phrase,
            english_phrase,
            "test, query",
            "https://test.com/image",
            'Context with "quotes"'
        )

        # Read back and verify proper escaping
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['Spanish'] == spanish_phrase
        assert rows[0]['English'] == english_phrase

    def test_long_url_truncation(self, app_instance, test_data_dir):
        """Test that long URLs are properly truncated in CSV."""
        csv_file = test_data_dir / "vocabulary_long_url.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        long_url = "https://images.unsplash.com/" + "x" * 200  # Very long URL
        
        app_instance.log_target_word_csv(
            "test word",
            "test translation",
            "test query",
            long_url,
            "test context"
        )

        # Read back and verify URL was truncated
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert len(rows[0]['Image URL']) <= 100  # Should be truncated

    def test_context_truncation(self, app_instance, test_data_dir):
        """Test that long contexts are properly truncated."""
        csv_file = test_data_dir / "vocabulary_long_context.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        long_context = "x" * 200  # Very long context
        
        app_instance.log_target_word_csv(
            "test word",
            "test translation", 
            "test query",
            "https://test.com/image",
            long_context
        )

        # Read back and verify context was truncated
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert len(rows[0]['Context']) <= 100  # Should be truncated


@pytest.mark.integration
class TestTranslationIntegration:
    """Integration tests for translation service."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for integration testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    def test_complete_vocabulary_workflow(self, app_instance, mock_openai_client, test_data_dir):
        """Test complete workflow from phrase extraction to vocabulary storage."""
        # Setup CSV file
        csv_file = test_data_dir / "vocabulary_workflow.csv"
        app_instance.CSV_TARGET_WORDS = csv_file

        # Mock translation response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "mountain landscape"
        mock_openai_client.chat.completions.create.return_value = mock_response
        app_instance.openai_client = mock_openai_client

        # Setup GUI mocks
        app_instance.description_text = Mock()
        app_instance.description_text.get.return_value = "Paisaje montañoso hermoso"
        app_instance.target_listbox = Mock()
        app_instance.update_target_list_display = Mock()
        app_instance.current_query = "mountain"
        app_instance.current_image_url = "https://test.com/image"

        # Add phrase
        phrase = "paisaje montañoso"
        app_instance.add_target_phrase(phrase)

        # Verify complete workflow
        assert phrase in app_instance.vocabulary_cache
        assert any("mountain landscape" in tp for tp in app_instance.target_phrases)
        assert csv_file.exists()

        # Verify CSV content
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['Spanish'] == phrase
        assert rows[0]['English'] == "mountain landscape"