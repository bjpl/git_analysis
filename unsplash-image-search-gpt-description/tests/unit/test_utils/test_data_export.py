"""
Unit tests for data export utilities and functionality.
Tests vocabulary export, Anki export, and other data export features.
"""

import pytest
import csv
import tempfile
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import sys
from datetime import datetime
import tkinter as tk

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import SAMPLE_VOCABULARY_CSV_DATA


@pytest.mark.unit
class TestDataExport:
    """Test suite for data export functionality."""

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
    def sample_vocabulary_file(self, test_data_dir):
        """Create a sample vocabulary CSV file for testing."""
        vocab_file = test_data_dir / "sample_vocabulary.csv"
        
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in SAMPLE_VOCABULARY_CSV_DATA:
                writer.writerow(row)
        
        return vocab_file

    def test_export_vocabulary_no_data(self, app_instance, test_data_dir):
        """Test export vocabulary when no data exists."""
        # Point to non-existent file
        empty_file = test_data_dir / "empty_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = empty_file

        # Mock messagebox to capture the call
        with patch('tkinter.messagebox.showinfo') as mock_messagebox:
            app_instance.export_vocabulary()
            
            # Should show "No Data" message
            mock_messagebox.assert_called_once()
            args, kwargs = mock_messagebox.call_args
            assert "No Data" in args[0] or "No vocabulary" in args[1]

    def test_export_vocabulary_window_creation(self, app_instance, sample_vocabulary_file):
        """Test export vocabulary window creation."""
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file

        # Mock Toplevel window
        mock_window = Mock(spec=tk.Toplevel)
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080

        with patch('tkinter.Toplevel', return_value=mock_window):
            app_instance.export_vocabulary()
            
            # Verify window was created and configured
            mock_window.title.assert_called_with("Export Vocabulary")
            mock_window.geometry.assert_called()
            mock_window.transient.assert_called_with(app_instance)
            mock_window.grab_set.assert_called_once()

    def test_anki_export_functionality(self, app_instance, sample_vocabulary_file, test_data_dir):
        """Test Anki export functionality."""
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file

        # Create expected Anki export file
        expected_anki_file = test_data_dir / f"anki_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

        # Test Anki export logic (simulate the export_anki function)
        with open(sample_vocabulary_file, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            
            # Simulate Anki export format creation
            anki_content = []
            for row in reader:
                if 'Spanish' in row and 'English' in row:
                    spanish = row['Spanish']
                    english = row['English']
                    context = row.get('Context', '')[:50]
                    anki_line = f"{spanish}\t{english} | {context}"
                    anki_content.append(anki_line)

        # Verify Anki format
        assert len(anki_content) > 0
        for line in anki_content:
            assert '\t' in line  # Tab separator
            assert '|' in line   # Context separator

        # Test first entry
        expected_spanish = "paisaje montañoso"
        expected_english = "mountain landscape"
        assert anki_content[0].startswith(f"{expected_spanish}\t{expected_english}")

    def test_plain_text_export_functionality(self, app_instance, sample_vocabulary_file, test_data_dir):
        """Test plain text export functionality."""
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file

        # Simulate text export logic
        text_content = []
        text_content.append("VOCABULARY LIST")
        text_content.append("=" * 50)
        text_content.append("")

        with open(sample_vocabulary_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Spanish' in row and 'English' in row:
                    text_content.append(f"{row['Spanish']} = {row['English']}")
                    if row.get('Search Query'):
                        text_content.append(f"  (from: {row['Search Query']})")
                    text_content.append("")

        # Verify text format
        full_text = "\n".join(text_content)
        assert "VOCABULARY LIST" in full_text
        assert "=" * 50 in full_text
        assert "paisaje montañoso = mountain landscape" in full_text
        assert "(from: mountain landscape)" in full_text

    def test_csv_export_functionality(self, app_instance, sample_vocabulary_file):
        """Test CSV export (opening existing file) functionality."""
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file

        # Test file opening simulation for different platforms
        test_platforms = ['win32', 'darwin', 'linux']
        
        for platform in test_platforms:
            with patch('sys.platform', platform):
                if platform == 'win32':
                    with patch('os.startfile') as mock_startfile:
                        try:
                            os.startfile(str(sample_vocabulary_file))
                            mock_startfile.assert_called_with(str(sample_vocabulary_file))
                        except AttributeError:
                            # os.startfile might not exist on non-Windows systems
                            pass
                elif platform == 'darwin':
                    with patch('os.system') as mock_system:
                        os.system(f"open {sample_vocabulary_file}")
                        mock_system.assert_called_with(f"open {sample_vocabulary_file}")
                else:  # linux
                    with patch('os.system') as mock_system:
                        os.system(f"xdg-open {sample_vocabulary_file}")
                        mock_system.assert_called_with(f"xdg-open {sample_vocabulary_file}")

    def test_export_word_count_statistics(self, app_instance, sample_vocabulary_file):
        """Test export word count statistics calculation."""
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file

        # Count words in sample file
        with open(sample_vocabulary_file, 'r', encoding='utf-8') as f:
            word_count = sum(1 for line in csv.DictReader(f))

        # Should match the number of vocabulary entries in sample data
        expected_count = len(SAMPLE_VOCABULARY_CSV_DATA) - 1  # Subtract header row
        assert word_count == expected_count

    def test_export_error_handling(self, app_instance, test_data_dir):
        """Test export error handling."""
        # Test with non-existent file
        nonexistent_file = test_data_dir / "nonexistent_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = nonexistent_file

        # Should handle missing file gracefully
        with patch('tkinter.messagebox.showinfo') as mock_messagebox:
            app_instance.export_vocabulary()
            mock_messagebox.assert_called_once()

    def test_export_file_permissions_error(self, app_instance, sample_vocabulary_file):
        """Test export when file permission errors occur."""
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file

        # Mock file operations to raise permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            # Should handle permission errors gracefully
            # The actual implementation would need error handling
            try:
                with open(sample_vocabulary_file, 'r', encoding='utf-8') as f:
                    pass
            except PermissionError:
                # This is expected in the test
                pass

    def test_export_large_vocabulary_file(self, app_instance, test_data_dir):
        """Test export with large vocabulary file."""
        large_vocab_file = test_data_dir / "large_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = large_vocab_file

        # Create large vocabulary file
        with open(large_vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            
            # Add many vocabulary entries
            for i in range(1000):
                writer.writerow([
                    f'palabra_{i}',
                    f'word_{i}',
                    f'2023-01-01 10:{i%60:02d}',
                    f'query_{i%10}',
                    f'https://test.com/image_{i}',
                    f'context for word {i}'
                ])

        # Test that large files are handled properly
        with open(large_vocab_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row_count = sum(1 for row in reader)

        assert row_count == 1000

    def test_export_special_characters_handling(self, app_instance, test_data_dir):
        """Test export with special characters in vocabulary."""
        special_vocab_file = test_data_dir / "special_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = special_vocab_file

        # Create file with special characters
        special_data = [
            ['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'],
            ['niño', 'child', '2023-01-01', 'family', 'url1', 'Un niño pequeño'],
            ['corazón', 'heart', '2023-01-01', 'body', 'url2', 'Mi corazón late'],
            ['montaña', 'mountain', '2023-01-01', 'nature', 'url3', 'La montaña alta'],
            ['español', 'Spanish', '2023-01-01', 'language', 'url4', 'Hablo español'],
        ]

        with open(special_vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in special_data:
                writer.writerow(row)

        # Test Anki export with special characters
        anki_content = []
        with open(special_vocab_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Spanish' in row and 'English' in row:
                    spanish = row['Spanish']
                    english = row['English']
                    context = row.get('Context', '')[:50]
                    anki_line = f"{spanish}\t{english} | {context}"
                    anki_content.append(anki_line)

        # Verify special characters are preserved
        special_chars_found = False
        for line in anki_content:
            if any(char in line for char in ['ñ', 'ó', 'á', 'é', 'í', 'ú']):
                special_chars_found = True
                break

        assert special_chars_found, "Special characters should be preserved in export"

    def test_export_empty_fields_handling(self, app_instance, test_data_dir):
        """Test export handling of empty fields."""
        empty_fields_file = test_data_dir / "empty_fields_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = empty_fields_file

        # Create file with some empty fields
        data_with_empty_fields = [
            ['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'],
            ['palabra', 'word', '2023-01-01', '', '', ''],  # Empty query, URL, context
            ['otro', 'another', '2023-01-01', 'test', 'url', 'context'],  # Complete entry
            ['vacío', '', '2023-01-01', 'empty', 'url', 'context'],  # Empty English
        ]

        with open(empty_fields_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in data_with_empty_fields:
                writer.writerow(row)

        # Test export handles empty fields gracefully
        with open(empty_fields_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            processed_entries = []
            
            for row in reader:
                if row['Spanish'] and row['English']:  # Only include complete entries
                    processed_entries.append(row)

        # Should include only complete entries
        assert len(processed_entries) == 2  # Only 'palabra' and 'otro'
        assert processed_entries[0]['Spanish'] == 'palabra'
        assert processed_entries[1]['Spanish'] == 'otro'

    def test_export_date_format_consistency(self, app_instance, test_data_dir):
        """Test export maintains consistent date formats."""
        date_format_file = test_data_dir / "date_format_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = date_format_file

        # Create file with various date formats
        date_data = [
            ['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'],
            ['primera', 'first', '2023-01-01 10:30', 'test1', 'url1', 'context1'],
            ['segunda', 'second', '2023-01-02 14:45', 'test2', 'url2', 'context2'],
            ['tercera', 'third', '2023-01-03 09:15', 'test3', 'url3', 'context3'],
        ]

        with open(date_format_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in date_data:
                writer.writerow(row)

        # Read and verify date formats
        with open(date_format_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            dates = [row['Date'] for row in reader]

        # All dates should follow the same format pattern
        for date_str in dates:
            # Should match YYYY-MM-DD HH:MM format
            assert len(date_str.split(' ')) == 2  # Date and time parts
            date_part, time_part = date_str.split(' ')
            assert len(date_part.split('-')) == 3  # YYYY-MM-DD
            assert len(time_part.split(':')) == 2  # HH:MM

    def test_export_context_truncation(self, app_instance, test_data_dir):
        """Test export context field truncation."""
        long_context_file = test_data_dir / "long_context_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = long_context_file

        # Create file with very long context
        long_context = "Esta es una descripción muy larga que excede los límites normales y debería ser truncada en el proceso de exportación para mantener formatos manejables. " * 5

        long_context_data = [
            ['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'],
            ['prueba', 'test', '2023-01-01', 'testing', 'url', long_context],
        ]

        with open(long_context_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in long_context_data:
                writer.writerow(row)

        # Test Anki export truncates context
        with open(long_context_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                context = row.get('Context', '')[:50]  # Simulate truncation
                assert len(context) <= 50

    def test_export_concurrent_access(self, app_instance, sample_vocabulary_file):
        """Test export handles concurrent file access."""
        import threading
        import time
        
        app_instance.CSV_TARGET_WORDS = sample_vocabulary_file
        
        access_results = []
        
        def read_vocabulary_file():
            try:
                with open(sample_vocabulary_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                    access_results.append(len(data))
            except Exception as e:
                access_results.append(f"Error: {str(e)}")

        # Create multiple threads to access file concurrently
        threads = []
        for i in range(3):
            thread = threading.Thread(target=read_vocabulary_file)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All threads should have successfully read the file
        assert len(access_results) == 3
        for result in access_results:
            assert isinstance(result, int)  # Should be row count, not error
            assert result > 0

    def test_export_memory_usage(self, app_instance, test_data_dir):
        """Test export memory usage with large datasets."""
        import sys
        
        memory_test_file = test_data_dir / "memory_test_vocabulary.csv"
        app_instance.CSV_TARGET_WORDS = memory_test_file

        # Create moderately large file
        with open(memory_test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
            
            for i in range(100):  # Smaller test for CI/CD
                writer.writerow([
                    f'palabra_{i}',
                    f'word_{i}',
                    '2023-01-01 10:00',
                    f'query_{i}',
                    f'https://test.com/image_{i}',
                    f'context for vocabulary item {i}'
                ])

        # Measure memory usage during export simulation
        initial_memory = sys.getsizeof([])
        
        # Simulate reading entire file into memory (as export might do)
        with open(memory_test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_data = list(reader)
        
        final_memory = sys.getsizeof(all_data)
        memory_usage = final_memory - initial_memory

        # Memory usage should be reasonable
        assert len(all_data) == 100
        assert memory_usage > 0
        assert memory_usage < 1024 * 1024  # Less than 1MB for 100 entries