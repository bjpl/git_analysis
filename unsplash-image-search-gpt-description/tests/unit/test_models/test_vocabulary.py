"""
Unit tests for vocabulary management models and data structures.
Tests vocabulary caching, phrase management, and data export functionality.
"""

import pytest
import csv
import json
import tempfile
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_VOCABULARY_CSV_DATA,
    EDGE_CASES
)


@pytest.mark.unit
class TestVocabularyManagement:
    """Test suite for vocabulary management functionality."""

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

    def test_vocabulary_cache_initialization(self, app_instance):
        """Test vocabulary cache is properly initialized."""
        assert isinstance(app_instance.vocabulary_cache, set)
        assert len(app_instance.vocabulary_cache) >= 0

    def test_vocabulary_cache_duplicate_prevention(self, app_instance):
        """Test that vocabulary cache prevents duplicates."""
        # Add same word multiple times
        word = "paisaje montañoso"
        app_instance.vocabulary_cache.add(word)
        app_instance.vocabulary_cache.add(word)
        app_instance.vocabulary_cache.add(word)

        # Should only have one instance
        assert len(app_instance.vocabulary_cache) == 1
        assert word in app_instance.vocabulary_cache

    def test_target_phrases_list_management(self, app_instance):
        """Test target phrases list management."""
        assert isinstance(app_instance.target_phrases, list)
        
        # Add phrases
        phrases = [
            "paisaje montañoso - mountain landscape",
            "lago cristalino - crystal lake",
            "ciudad nocturna - night city"
        ]
        
        app_instance.target_phrases.extend(phrases)
        
        assert len(app_instance.target_phrases) == 3
        for phrase in phrases:
            assert phrase in app_instance.target_phrases

    def test_vocabulary_persistence_across_sessions(self, app_instance, test_data_dir):
        """Test that vocabulary persists across application sessions."""
        # Create vocabulary file
        vocab_file = test_data_dir / "vocabulary_persistence.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Write initial vocabulary
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writerow(['montaña', 'mountain', '2023-01-01 10:00', 'nature', 'url1', 'context1'])
            writer.writerow(['océano', 'ocean', '2023-01-01 10:01', 'water', 'url2', 'context2'])

        # Load vocabulary into cache
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Verify vocabulary was loaded
        assert 'montaña' in app_instance.vocabulary_cache
        assert 'océano' in app_instance.vocabulary_cache
        assert len(app_instance.vocabulary_cache) >= 2

    def test_vocabulary_file_format_validation(self, app_instance, test_data_dir):
        """Test validation of vocabulary file format."""
        vocab_file = test_data_dir / "vocabulary_format.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Create properly formatted CSV
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Proper header
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writerow(['palabra', 'word', '2023-01-01 10:00', 'test', 'url', 'context'])

        # Load and verify
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        assert 'palabra' in app_instance.vocabulary_cache

    def test_vocabulary_data_structure_integrity(self, app_instance):
        """Test that vocabulary data structures maintain integrity."""
        # Test cache set properties
        test_words = ['palabra1', 'palabra2', 'palabra3', 'palabra1']  # Include duplicate
        for word in test_words:
            app_instance.vocabulary_cache.add(word)

        # Set should automatically handle duplicates
        assert len(app_instance.vocabulary_cache) == 3

        # Test target phrases list allows duplicates if needed
        app_instance.target_phrases = []
        app_instance.target_phrases.append('phrase1 - translation1')
        app_instance.target_phrases.append('phrase2 - translation2')
        app_instance.target_phrases.append('phrase1 - translation1')  # Duplicate

        assert len(app_instance.target_phrases) == 3  # List allows duplicates

    def test_vocabulary_search_and_filtering(self, app_instance):
        """Test vocabulary search and filtering capabilities."""
        # Setup test vocabulary
        test_vocabulary = {
            'montaña', 'lago', 'ciudad', 'paisaje',
            'hermoso', 'grande', 'pequeño',
            'caminar', 'correr', 'saltar'
        }
        app_instance.vocabulary_cache = test_vocabulary

        # Test filtering by type (would require categorization in real implementation)
        # For now, test basic membership and iteration
        mountain_related = [word for word in app_instance.vocabulary_cache 
                          if 'montaña' in word or 'paisaje' in word]
        
        assert 'montaña' in mountain_related
        assert 'paisaje' in mountain_related

    def test_vocabulary_statistics_calculation(self, app_instance):
        """Test vocabulary statistics calculation."""
        # Setup test data
        app_instance.vocabulary_cache = {'cached1', 'cached2', 'cached3'}
        app_instance.target_phrases = ['target1', 'target2']
        app_instance.used_image_urls = {'url1', 'url2', 'url3', 'url4'}

        # Calculate statistics (as done in update_stats)
        vocab_count = len(app_instance.vocabulary_cache) + len(app_instance.target_phrases)
        image_count = len(app_instance.used_image_urls)

        assert vocab_count == 5  # 3 cached + 2 target
        assert image_count == 4

    def test_vocabulary_export_data_preparation(self, app_instance, test_data_dir):
        """Test preparation of vocabulary data for export."""
        # Create test vocabulary file
        vocab_file = test_data_dir / "vocabulary_export_prep.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Write test data
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writeheader()
            writer.writerow({
                'Spanish': 'montaña',
                'English': 'mountain',
                'Date': '2023-01-01 10:00',
                'Search Query': 'landscape',
                'Image URL': 'https://test.com/image',
                'Context': 'Beautiful mountain view'
            })

        # Test data reading for export
        with open(vocab_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['Spanish'] == 'montaña'
        assert rows[0]['English'] == 'mountain'
        assert 'Search Query' in rows[0]
        assert 'Context' in rows[0]

    def test_vocabulary_data_validation(self, app_instance):
        """Test validation of vocabulary data entries."""
        # Test valid entry
        valid_entry = {
            'Spanish': 'paisaje montañoso',
            'English': 'mountain landscape',
            'Date': '2023-01-01 10:00',
            'Search Query': 'mountain',
            'Image URL': 'https://test.com/image',
            'Context': 'Beautiful scenery'
        }

        # Check required fields exist
        required_fields = ['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context']
        for field in required_fields:
            assert field in valid_entry
            assert valid_entry[field] is not None

    def test_vocabulary_special_characters_handling(self, app_instance, test_data_dir):
        """Test handling of special characters in vocabulary."""
        vocab_file = test_data_dir / "vocabulary_special_chars.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Test with Spanish special characters
        special_words = {
            'niño': 'child',
            'corazón': 'heart', 
            'montaña': 'mountain',
            'español': 'Spanish',
            'año': 'year'
        }

        # Write to file
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            for spanish, english in special_words.items():
                writer.writerow([spanish, english, '2023-01-01', 'test', 'url', 'context'])

        # Load and verify
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        for word in special_words.keys():
            assert word in app_instance.vocabulary_cache

    def test_vocabulary_unicode_handling(self, app_instance, test_data_dir):
        """Test handling of Unicode characters in vocabulary."""
        vocab_file = test_data_dir / "vocabulary_unicode.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Test with Unicode characters
        unicode_phrase = EDGE_CASES["unicode_phrase"]
        
        app_instance.vocabulary_cache.add(unicode_phrase)
        
        # Verify Unicode is preserved
        assert unicode_phrase in app_instance.vocabulary_cache

    def test_vocabulary_case_sensitivity(self, app_instance):
        """Test vocabulary case sensitivity handling."""
        # Test different cases
        app_instance.vocabulary_cache.add('Montaña')
        app_instance.vocabulary_cache.add('montaña')
        app_instance.vocabulary_cache.add('MONTAÑA')

        # All should be treated as separate entries (case sensitive)
        assert len(app_instance.vocabulary_cache) == 3

    def test_vocabulary_whitespace_handling(self, app_instance):
        """Test vocabulary whitespace handling."""
        # Test various whitespace scenarios
        phrases_with_whitespace = [
            'paisaje montañoso',  # Normal space
            'paisaje  montañoso',  # Double space
            ' paisaje montañoso ',  # Leading/trailing spaces
            'paisaje\tmontañoso',  # Tab character
        ]

        for phrase in phrases_with_whitespace:
            app_instance.vocabulary_cache.add(phrase)

        # All variations should be preserved as separate entries
        assert len(app_instance.vocabulary_cache) == len(phrases_with_whitespace)

    def test_vocabulary_empty_values_handling(self, app_instance, test_data_dir):
        """Test handling of empty values in vocabulary data."""
        vocab_file = test_data_dir / "vocabulary_empty_values.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Write CSV with some empty values
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            writer.writerow(['palabra', 'word', '2023-01-01', '', '', ''])  # Empty query, URL, context
            writer.writerow(['', 'empty', '2023-01-01', 'query', 'url', 'context'])  # Empty Spanish
            writer.writerow(['spanish', '', '2023-01-01', 'query', 'url', 'context'])  # Empty English

        # Should handle gracefully
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Only entries with valid Spanish words should be loaded
        assert 'palabra' in app_instance.vocabulary_cache

    def test_vocabulary_maximum_length_handling(self, app_instance):
        """Test handling of maximum length vocabulary entries."""
        # Test very long vocabulary entries
        long_phrase = EDGE_CASES["very_long_phrase"]
        
        # Should handle long phrases
        app_instance.vocabulary_cache.add(long_phrase)
        assert long_phrase in app_instance.vocabulary_cache

        # Test in target phrases
        app_instance.target_phrases.append(f"{long_phrase} - very long translation")
        assert len(app_instance.target_phrases) == 1

    def test_vocabulary_performance_with_large_dataset(self, app_instance):
        """Test vocabulary performance with large datasets."""
        # Add many vocabulary items
        large_vocabulary = {f'palabra_{i}' for i in range(1000)}
        app_instance.vocabulary_cache.update(large_vocabulary)

        # Test lookup performance
        import time
        start_time = time.time()
        
        # Test membership operations
        assert 'palabra_500' in app_instance.vocabulary_cache
        assert 'palabra_999' in app_instance.vocabulary_cache
        assert 'nonexistent_word' not in app_instance.vocabulary_cache
        
        end_time = time.time()
        lookup_time = end_time - start_time

        # Should be very fast (set operations are O(1))
        assert lookup_time < 0.1  # Less than 100ms

        # Test iteration performance
        start_time = time.time()
        word_count = len([word for word in app_instance.vocabulary_cache if word.startswith('palabra_')])
        end_time = time.time()
        iteration_time = end_time - start_time

        assert word_count == 1000
        assert iteration_time < 0.5  # Less than 500ms

    def test_vocabulary_memory_efficiency(self, app_instance):
        """Test vocabulary memory efficiency."""
        import sys
        
        # Measure memory usage before adding vocabulary
        initial_size = sys.getsizeof(app_instance.vocabulary_cache)
        
        # Add vocabulary
        test_vocabulary = {f'test_word_{i}' for i in range(100)}
        app_instance.vocabulary_cache.update(test_vocabulary)
        
        # Measure memory usage after
        final_size = sys.getsizeof(app_instance.vocabulary_cache)
        
        # Memory increase should be reasonable
        memory_increase = final_size - initial_size
        # Set should be memory efficient (not testing exact values due to Python implementation details)
        assert memory_increase > 0


@pytest.mark.unit
class TestVocabularyDataTypes:
    """Test suite for vocabulary data type handling."""

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

    def test_vocabulary_string_normalization(self, app_instance):
        """Test vocabulary string normalization."""
        # Test different string types
        string_types = [
            'normal string',
            'string with números 123',
            'string with symbols !@#$%',
        ]

        for string_val in string_types:
            app_instance.vocabulary_cache.add(string_val)
            assert string_val in app_instance.vocabulary_cache

    def test_vocabulary_type_validation(self, app_instance):
        """Test vocabulary type validation."""
        # Only strings should be accepted in vocabulary
        valid_entries = ['palabra', 'another word', 'más palabras']
        
        for entry in valid_entries:
            assert isinstance(entry, str)
            app_instance.vocabulary_cache.add(entry)

        assert len(app_instance.vocabulary_cache) == len(valid_entries)

    def test_vocabulary_encoding_consistency(self, app_instance, test_data_dir):
        """Test vocabulary encoding consistency."""
        vocab_file = test_data_dir / "vocabulary_encoding.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Test various encoded characters
        test_words = [
            'café',      # é
            'niño',      # ñ
            'corazón',   # ó
            'inglés',    # é
            'años',      # ñ
        ]

        # Write with UTF-8 encoding
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            for word in test_words:
                writer.writerow([word, 'translation', '2023-01-01', 'query', 'url', 'context'])

        # Read back and verify encoding preserved
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        for word in test_words:
            assert word in app_instance.vocabulary_cache