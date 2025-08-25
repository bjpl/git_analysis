"""
Integration tests for data persistence functionality.
Tests complete data flow from memory to file storage and retrieval.
"""

import pytest
import json
import csv
import tempfile
import shutil
from unittest.mock import Mock, patch
from pathlib import Path
import sys
from datetime import datetime
import time

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import ImageSearchApp
from tests.fixtures.sample_data import (
    SAMPLE_SESSION_DATA,
    SAMPLE_VOCABULARY_CSV_DATA,
    create_sample_files
)


@pytest.mark.integration
class TestDataPersistence:
    """Test suite for data persistence and storage functionality."""

    @pytest.fixture
    def app_instance(self, mock_config_manager, tkinter_root):
        """Create ImageSearchApp instance for data persistence testing."""
        with patch('main.ensure_api_keys_configured', return_value=mock_config_manager):
            app = ImageSearchApp()
            app.withdraw()
            yield app
            try:
                app.destroy()
            except:
                pass

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for data persistence tests."""
        temp_dir = tempfile.mkdtemp(prefix="data_persistence_test_")
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_complete_session_persistence_cycle(self, app_instance, temp_data_dir):
        """Test complete session data persistence from creation to retrieval."""
        # Setup file paths
        session_file = temp_data_dir / "session_cycle.json"
        vocab_file = temp_data_dir / "vocab_cycle.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Step 1: Create session data
        session_data = [
            {
                "timestamp": datetime.now().isoformat(),
                "query": "persistence test",
                "image_url": "https://test.com/persistence_image",
                "user_note": "Testing data persistence",
                "generated_description": "Una descripción de prueba para persistencia de datos"
            }
        ]
        app_instance.log_entries = session_data
        app_instance.target_phrases = ["prueba - test", "persistencia - persistence"]

        # Step 2: Save session data
        app_instance.save_session_to_json()

        # Verify session file was created
        assert session_file.exists()

        # Step 3: Clear in-memory data
        app_instance.log_entries = []
        app_instance.used_image_urls.clear()

        # Step 4: Load session data back
        app_instance.load_used_image_urls_from_log()

        # Verify data was loaded
        canonical_url = app_instance.canonicalize_url("https://test.com/persistence_image")
        assert canonical_url in app_instance.used_image_urls

        # Step 5: Verify file contents
        with open(session_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert "sessions" in loaded_data
        assert len(loaded_data["sessions"]) == 1
        session = loaded_data["sessions"][0]
        assert len(session["entries"]) == 1
        assert session["entries"][0]["query"] == "persistence test"

    def test_vocabulary_persistence_cycle(self, app_instance, temp_data_dir):
        """Test complete vocabulary persistence from memory to CSV and back."""
        vocab_file = temp_data_dir / "vocab_persistence.csv"
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Step 1: Add vocabulary to memory
        test_vocabulary = [
            ("montaña", "mountain"),
            ("río", "river"),
            ("bosque", "forest"),
            ("cielo", "sky")
        ]

        # Simulate adding vocabulary through the normal workflow
        for spanish, english in test_vocabulary:
            # Add to cache and CSV
            app_instance.vocabulary_cache.add(spanish)
            app_instance.log_target_word_csv(
                spanish,
                english,
                "persistence test",
                "https://test.com/image",
                f"Context for {spanish}"
            )

        # Step 2: Verify CSV file was created and populated
        assert vocab_file.exists()

        with open(vocab_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == len(test_vocabulary)
        for i, (spanish, english) in enumerate(test_vocabulary):
            assert rows[i]["Spanish"] == spanish
            assert rows[i]["English"] == english

        # Step 3: Clear memory cache
        app_instance.vocabulary_cache.clear()
        assert len(app_instance.vocabulary_cache) == 0

        # Step 4: Reload from file
        app_instance.load_vocabulary_cache()

        # Step 5: Verify all vocabulary was loaded back
        for spanish, english in test_vocabulary:
            assert spanish in app_instance.vocabulary_cache

    def test_concurrent_data_persistence(self, app_instance, temp_data_dir):
        """Test data persistence under concurrent access."""
        import threading
        
        session_file = temp_data_dir / "concurrent_session.json"
        vocab_file = temp_data_dir / "concurrent_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        errors = []
        successful_operations = []

        def add_session_data(thread_id, count):
            try:
                for i in range(count):
                    entry = {
                        "timestamp": datetime.now().isoformat(),
                        "query": f"thread_{thread_id}_query_{i}",
                        "image_url": f"https://test.com/thread_{thread_id}_image_{i}",
                        "user_note": f"Thread {thread_id} note {i}",
                        "generated_description": f"Descripción del hilo {thread_id} item {i}"
                    }
                    app_instance.log_entries.append(entry)
                    successful_operations.append(f"thread_{thread_id}_entry_{i}")
                    
                    # Add some delay to simulate real conditions
                    time.sleep(0.01)
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")

        def add_vocabulary_data(thread_id, count):
            try:
                for i in range(count):
                    spanish = f"palabra_{thread_id}_{i}"
                    english = f"word_{thread_id}_{i}"
                    app_instance.vocabulary_cache.add(spanish)
                    app_instance.log_target_word_csv(
                        spanish,
                        english,
                        f"query_{thread_id}",
                        f"https://test.com/image_{thread_id}_{i}",
                        f"Context {thread_id} {i}"
                    )
                    successful_operations.append(f"thread_{thread_id}_vocab_{i}")
                    
                    time.sleep(0.01)
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")

        # Create threads for concurrent operations
        threads = []
        for i in range(3):
            session_thread = threading.Thread(target=add_session_data, args=(i, 5))
            vocab_thread = threading.Thread(target=add_vocabulary_data, args=(i, 5))
            threads.extend([session_thread, vocab_thread])

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent operation errors: {errors}"

        # Verify all operations completed
        assert len(successful_operations) == 30  # 3 threads * (5 session + 5 vocab)

        # Save final data
        app_instance.save_session_to_json()

        # Verify final state
        assert session_file.exists()
        assert vocab_file.exists()

        # Check session file
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        assert len(session_data["sessions"]) == 1
        assert len(session_data["sessions"][0]["entries"]) == 15  # 3 threads * 5 entries

        # Check vocabulary file
        with open(vocab_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            vocab_rows = list(reader)
        assert len(vocab_rows) == 15  # 3 threads * 5 vocabulary items

    def test_data_recovery_from_corruption(self, app_instance, temp_data_dir):
        """Test data recovery mechanisms when files are corrupted."""
        session_file = temp_data_dir / "corrupted_session.json"
        vocab_file = temp_data_dir / "corrupted_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Step 1: Create valid data first
        app_instance.log_entries = [{
            "timestamp": datetime.now().isoformat(),
            "query": "recovery test",
            "image_url": "https://test.com/recovery",
            "user_note": "Test note",
            "generated_description": "Test description"
        }]
        app_instance.save_session_to_json()

        app_instance.vocabulary_cache.add("recuperación")
        app_instance.log_target_word_csv(
            "recuperación",
            "recovery",
            "recovery test",
            "https://test.com/recovery",
            "Recovery context"
        )

        # Verify files were created properly
        assert session_file.exists()
        assert vocab_file.exists()

        # Step 2: Corrupt the files
        with open(session_file, 'w') as f:
            f.write("invalid json content {corrupted")

        with open(vocab_file, 'w') as f:
            f.write("corrupted,csv,content\nwith\"broken\"quotes\nand,incomplete")

        # Step 3: Attempt to load corrupted data
        app_instance.log_entries = []
        app_instance.used_image_urls.clear()
        app_instance.vocabulary_cache.clear()

        # Should handle corrupted session file gracefully
        app_instance.load_used_image_urls_from_log()
        # No exception should be raised, used_image_urls should remain empty
        assert len(app_instance.used_image_urls) == 0

        # Should handle corrupted vocabulary file gracefully
        app_instance.load_vocabulary_cache()
        # May have partial data or be empty, but should not crash

        # Step 4: Verify recovery by creating new data
        # Should be able to create new valid data after corruption
        app_instance.log_entries = [{
            "timestamp": datetime.now().isoformat(),
            "query": "recovery success",
            "image_url": "https://test.com/recovery_success",
            "user_note": "Recovery successful",
            "generated_description": "Recovery description"
        }]

        # Should recreate valid files
        app_instance.save_session_to_json()
        app_instance.log_target_word_csv(
            "éxito",
            "success", 
            "recovery",
            "https://test.com/success",
            "Success context"
        )

        # Verify new files are valid
        with open(session_file, 'r', encoding='utf-8') as f:
            recovered_data = json.load(f)  # Should not raise exception
        assert "sessions" in recovered_data

    def test_large_dataset_persistence(self, app_instance, temp_data_dir):
        """Test persistence of large datasets."""
        session_file = temp_data_dir / "large_session.json"
        vocab_file = temp_data_dir / "large_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Create large session data
        large_session_entries = []
        for i in range(100):
            entry = {
                "timestamp": datetime.now().isoformat(),
                "query": f"large_test_query_{i}",
                "image_url": f"https://test.com/large_image_{i}",
                "user_note": f"Large test note {i} with some additional content to make it longer",
                "generated_description": f"Descripción larga número {i} con contenido adicional para simular descripciones reales generadas por GPT que pueden ser bastante extensas y detalladas."
            }
            large_session_entries.append(entry)

        app_instance.log_entries = large_session_entries

        # Create large vocabulary dataset
        large_vocabulary = []
        for i in range(500):
            spanish_word = f"palabra_grande_{i}"
            english_word = f"large_word_{i}"
            app_instance.vocabulary_cache.add(spanish_word)
            large_vocabulary.append((spanish_word, english_word))

        # Measure persistence performance
        start_time = time.time()

        # Save large session
        app_instance.save_session_to_json()

        # Save large vocabulary
        for spanish, english in large_vocabulary:
            app_instance.log_target_word_csv(
                spanish,
                english,
                f"large_query_{hash(spanish) % 10}",
                f"https://test.com/large_{hash(spanish) % 100}",
                f"Context for {spanish}"
            )

        end_time = time.time()
        persistence_time = end_time - start_time

        # Verify files were created
        assert session_file.exists()
        assert vocab_file.exists()

        # Verify file sizes are reasonable
        session_size = session_file.stat().st_size
        vocab_size = vocab_file.stat().st_size

        assert session_size > 10000  # Should be substantial
        assert vocab_size > 20000    # Should be substantial

        # Performance should be reasonable
        assert persistence_time < 10.0  # Should complete within 10 seconds

        # Test loading large datasets
        app_instance.log_entries = []
        app_instance.used_image_urls.clear()
        app_instance.vocabulary_cache.clear()

        start_time = time.time()

        app_instance.load_used_image_urls_from_log()
        app_instance.load_vocabulary_cache()

        end_time = time.time()
        loading_time = end_time - start_time

        # Verify data was loaded
        assert len(app_instance.used_image_urls) == 100
        assert len(app_instance.vocabulary_cache) >= 500

        # Loading performance should be reasonable
        assert loading_time < 5.0  # Should load within 5 seconds

    def test_cross_session_data_consistency(self, app_instance, temp_data_dir):
        """Test data consistency across multiple application sessions."""
        session_file = temp_data_dir / "cross_session.json"
        vocab_file = temp_data_dir / "cross_session_vocab.csv"
        
        # Session 1: Create and save initial data
        app1_session_data = [{
            "timestamp": "2023-01-01T10:00:00",
            "query": "session_1_query",
            "image_url": "https://test.com/session_1_image",
            "user_note": "Session 1 note",
            "generated_description": "Session 1 description"
        }]

        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file
        app_instance.log_entries = app1_session_data
        app_instance.vocabulary_cache.add("sesión")
        
        # Save session 1 data
        app_instance.save_session_to_json()
        app_instance.log_target_word_csv(
            "sesión",
            "session",
            "session_1_query",
            "https://test.com/session_1_image",
            "Session context"
        )

        # Simulate new application instance (Session 2)
        with patch('main.ensure_api_keys_configured', return_value=app_instance.config_manager):
            app2 = ImageSearchApp()
            app2.withdraw()
            app2.LOG_FILENAME = session_file
            app2.CSV_TARGET_WORDS = vocab_file

        try:
            # Session 2: Load existing data
            app2.load_used_image_urls_from_log()
            app2.load_vocabulary_cache()

            # Verify session 1 data was loaded
            assert "https://test.com/session_1_image" in app2.used_image_urls
            assert "sesión" in app2.vocabulary_cache

            # Add session 2 data
            app2_session_data = [{
                "timestamp": "2023-01-01T11:00:00",
                "query": "session_2_query", 
                "image_url": "https://test.com/session_2_image",
                "user_note": "Session 2 note",
                "generated_description": "Session 2 description"
            }]

            app2.log_entries = app2_session_data
            app2.vocabulary_cache.add("segunda")
            
            # Save session 2 data
            app2.save_session_to_json()
            app2.log_target_word_csv(
                "segunda",
                "second",
                "session_2_query",
                "https://test.com/session_2_image",
                "Second context"
            )

            # Verify combined data in files
            with open(session_file, 'r', encoding='utf-8') as f:
                combined_sessions = json.load(f)

            assert len(combined_sessions["sessions"]) == 2
            assert combined_sessions["sessions"][0]["entries"][0]["query"] == "session_1_query"
            assert combined_sessions["sessions"][1]["entries"][0]["query"] == "session_2_query"

            # Verify vocabulary file has both entries
            with open(vocab_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                vocab_rows = list(reader)

            assert len(vocab_rows) == 2
            spanish_words = {row["Spanish"] for row in vocab_rows}
            assert "sesión" in spanish_words
            assert "segunda" in spanish_words

        finally:
            app2.destroy()

    def test_data_migration_compatibility(self, app_instance, temp_data_dir):
        """Test backward compatibility with different data formats."""
        session_file = temp_data_dir / "migration_session.json"
        vocab_file = temp_data_dir / "migration_vocab.csv"
        app_instance.LOG_FILENAME = session_file
        app_instance.CSV_TARGET_WORDS = vocab_file

        # Test 1: Old text format session log (backward compatibility)
        old_text_content = """
=== Informe de Sesión ===
Fecha: 2023-01-01 10:00:00

Entrada 1:
  Consulta de la Búsqueda: old format test
  URL de la Imagen     : https://test.com/old_format_image
  Notas del Usuario    : Old format note
  Descripción Generada : Old format description
----------------------------------------
Target Phrases: palabra_antigua - old_word
"""
        
        # Write old format to session file  
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(old_text_content)

        # Should handle old format gracefully
        app_instance.load_used_image_urls_from_log()
        
        # Should extract URLs from old format
        assert "https://test.com/old_format_image" in app_instance.used_image_urls

        # Test 2: Old vocabulary format (no headers)
        with open(vocab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # No headers, just data
            writer.writerow(['palabra_vieja', 'old_word'])
            writer.writerow(['término_antiguo', 'ancient_term'])

        # Should handle old format
        app_instance.vocabulary_cache.clear()
        app_instance.load_vocabulary_cache()

        # Should extract vocabulary from old format
        # (behavior depends on implementation - might be empty or have partial data)

        # Test 3: Migration to new format
        app_instance.log_entries = [{
            "timestamp": datetime.now().isoformat(),
            "query": "migration test",
            "image_url": "https://test.com/migration_image",
            "user_note": "Migration note",
            "generated_description": "Migration description"
        }]

        # Save in new format (should replace old format)
        app_instance.save_session_to_json()

        # Verify new format
        with open(session_file, 'r', encoding='utf-8') as f:
            new_format_data = json.load(f)

        assert "sessions" in new_format_data
        assert len(new_format_data["sessions"]) == 1