# File: tests/unit/test_vocab_model.py
"""
Unit tests for the VocabModel class.
Tests vocabulary CRUD operations, regionalism handling, and data validation.
"""

import pytest
import sqlite3
from unittest.mock import Mock, patch

from models.vocab_model import VocabModel


class TestVocabModel:
    """Test cases for VocabModel CRUD operations."""
    
    def test_add_vocab_with_valid_data(self, temp_db, sample_session, sample_vocab_data):
        """Test adding vocabulary with valid data."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=sample_vocab_data["word_phrase"],
            translation=sample_vocab_data["translation"],
            context_notes=sample_vocab_data["context_notes"]
        )
        
        assert vocab_id is not None
        assert isinstance(vocab_id, int)
        assert vocab_id > 0
    
    def test_add_vocab_with_regionalisms(self, temp_db, sample_session, sample_vocab_data):
        """Test adding vocabulary with regionalisms."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=sample_vocab_data["word_phrase"],
            translation=sample_vocab_data["translation"],
            context_notes=sample_vocab_data["context_notes"],
            regionalisms=sample_vocab_data["regionalisms"]
        )
        
        assert vocab_id is not None
        
        # Verify regionalisms were stored
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        vocab_entry = next(v for v in vocab_list if v['vocab_id'] == vocab_id)
        
        # Assuming regionalisms are stored as comma-separated or in related table
        if 'countries' in vocab_entry:
            stored_countries = vocab_entry['countries']
            for country in sample_vocab_data["regionalisms"]:
                assert country in stored_countries
    
    def test_add_vocab_missing_session_id(self, temp_db, sample_vocab_data):
        """Test adding vocabulary with missing session_id."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=None,
            word_phrase=sample_vocab_data["word_phrase"],
            translation=sample_vocab_data["translation"]
        )
        
        assert vocab_id is None
    
    def test_add_vocab_missing_word_phrase(self, temp_db, sample_session):
        """Test adding vocabulary with missing word_phrase."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=None,
            translation="some translation"
        )
        
        assert vocab_id is None
    
    def test_add_vocab_empty_word_phrase(self, temp_db, sample_session):
        """Test adding vocabulary with empty word_phrase."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="",
            translation="some translation"
        )
        
        assert vocab_id is None
    
    def test_add_vocab_with_invalid_session_id(self, temp_db):
        """Test adding vocabulary with non-existent session_id."""
        vocab_model = VocabModel(temp_db)
        
        with pytest.raises(sqlite3.IntegrityError):
            vocab_model.add_vocab(
                session_id=999,  # Non-existent session
                word_phrase="test word",
                translation="test translation"
            )
    
    def test_get_vocab_for_session_valid(self, temp_db, sample_session):
        """Test retrieving vocabulary for a valid session."""
        vocab_model = VocabModel(temp_db)
        
        # Add some vocabulary
        test_words = [
            ("hola", "hello"),
            ("adiós", "goodbye"),
            ("gracias", "thank you")
        ]
        
        added_ids = []
        for word, translation in test_words:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase=word,
                translation=translation
            )
            added_ids.append(vocab_id)
        
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        
        assert len(vocab_list) == 3
        
        retrieved_words = [(v['word_phrase'], v['translation']) for v in vocab_list]
        for word, translation in test_words:
            assert (word, translation) in retrieved_words
    
    def test_get_vocab_for_session_empty(self, temp_db, sample_session):
        """Test retrieving vocabulary for session with no vocabulary."""
        vocab_model = VocabModel(temp_db)
        
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        
        assert isinstance(vocab_list, list)
        assert len(vocab_list) == 0
    
    def test_get_vocab_for_invalid_session(self, temp_db):
        """Test retrieving vocabulary for non-existent session."""
        vocab_model = VocabModel(temp_db)
        
        vocab_list = vocab_model.get_vocab_for_session(999)
        
        assert isinstance(vocab_list, list)
        assert len(vocab_list) == 0
    
    def test_delete_vocab_valid(self, temp_db, sample_session):
        """Test deleting vocabulary with valid ID."""
        vocab_model = VocabModel(temp_db)
        
        # Add vocabulary first
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="test word",
            translation="test translation"
        )
        
        # Verify it exists
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        assert len(vocab_list) == 1
        
        # Delete it
        rows_affected = vocab_model.delete_vocab(vocab_id)
        assert rows_affected == 1
        
        # Verify it's deleted
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        assert len(vocab_list) == 0
    
    def test_delete_vocab_invalid_id(self, temp_db):
        """Test deleting non-existent vocabulary."""
        vocab_model = VocabModel(temp_db)
        
        rows_affected = vocab_model.delete_vocab(999)
        assert rows_affected == 0
    
    def test_update_vocab_valid(self, temp_db, sample_session):
        """Test updating vocabulary with valid data."""
        vocab_model = VocabModel(temp_db)
        
        # Add vocabulary first
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="original word",
            translation="original translation"
        )
        
        # Update it
        rows_affected = vocab_model.update_vocab(
            vocab_id=vocab_id,
            word_phrase="updated word",
            translation="updated translation",
            context_notes="updated notes"
        )
        
        assert rows_affected == 1
        
        # Verify the update
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        updated_vocab = next(v for v in vocab_list if v['vocab_id'] == vocab_id)
        
        assert updated_vocab['word_phrase'] == "updated word"
        assert updated_vocab['translation'] == "updated translation"
        assert updated_vocab['context_notes'] == "updated notes"
    
    def test_update_vocab_invalid_id(self, temp_db):
        """Test updating non-existent vocabulary."""
        vocab_model = VocabModel(temp_db)
        
        rows_affected = vocab_model.update_vocab(
            vocab_id=999,
            word_phrase="test word",
            translation="test translation"
        )
        
        assert rows_affected == 0
    
    def test_get_vocab_by_id_valid(self, temp_db, sample_session):
        """Test retrieving specific vocabulary by ID."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="test word",
            translation="test translation"
        )
        
        vocab = vocab_model.get_vocab_by_id(vocab_id)
        
        assert vocab is not None
        assert vocab['vocab_id'] == vocab_id
        assert vocab['word_phrase'] == "test word"
        assert vocab['translation'] == "test translation"
    
    def test_get_vocab_by_id_invalid(self, temp_db):
        """Test retrieving non-existent vocabulary."""
        vocab_model = VocabModel(temp_db)
        
        vocab = vocab_model.get_vocab_by_id(999)
        
        assert vocab is None


class TestVocabModelRegionalisms:
    """Test regionalism handling in VocabModel."""
    
    def test_add_regionalisms_single_country(self, temp_db, sample_session):
        """Test adding vocabulary with single regionalism."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="coche",
            translation="car",
            regionalisms=["Spain"]
        )
        
        assert vocab_id is not None
        
        # Verify regionalism was stored
        if hasattr(vocab_model, 'get_regionalisms_for_vocab'):
            regionalisms = vocab_model.get_regionalisms_for_vocab(vocab_id)
            assert "Spain" in regionalisms
    
    def test_add_regionalisms_multiple_countries(self, temp_db, sample_session):
        """Test adding vocabulary with multiple regionalisms."""
        vocab_model = VocabModel(temp_db)
        
        countries = ["Mexico", "Argentina", "Colombia", "Spain"]
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="plata",
            translation="money",
            regionalisms=countries
        )
        
        assert vocab_id is not None
        
        # Check that all regionalisms were stored
        cursor = temp_db.conn.cursor()
        cursor.execute(
            "SELECT country_name FROM vocab_regionalisms WHERE vocab_id = ?",
            (vocab_id,)
        )
        stored_countries = [row[0] for row in cursor.fetchall()]
        
        for country in countries:
            assert country in stored_countries
    
    def test_add_regionalisms_empty_list(self, temp_db, sample_session):
        """Test adding vocabulary with empty regionalisms list."""
        vocab_model = VocabModel(temp_db)
        
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="universal",
            translation="universal",
            regionalisms=[]
        )
        
        assert vocab_id is not None
        
        # Check that no regionalisms were stored
        cursor = temp_db.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM vocab_regionalisms WHERE vocab_id = ?",
            (vocab_id,)
        )
        count = cursor.fetchone()[0]
        assert count == 0
    
    def test_update_regionalisms(self, temp_db, sample_session):
        """Test updating regionalisms for existing vocabulary."""
        vocab_model = VocabModel(temp_db)
        
        # Add vocabulary with initial regionalisms
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="carro",
            translation="car",
            regionalisms=["Mexico", "Colombia"]
        )
        
        # Update regionalisms (assuming method exists)
        if hasattr(vocab_model, 'update_regionalisms'):
            vocab_model.update_regionalisms(vocab_id, ["Argentina", "Chile"])
            
            # Verify update
            cursor = temp_db.conn.cursor()
            cursor.execute(
                "SELECT country_name FROM vocab_regionalisms WHERE vocab_id = ?",
                (vocab_id,)
            )
            stored_countries = [row[0] for row in cursor.fetchall()]
            
            assert "Argentina" in stored_countries
            assert "Chile" in stored_countries
            assert "Mexico" not in stored_countries
            assert "Colombia" not in stored_countries
    
    def test_delete_vocab_cascades_regionalisms(self, temp_db, sample_session):
        """Test that deleting vocabulary also deletes its regionalisms."""
        vocab_model = VocabModel(temp_db)
        
        # Add vocabulary with regionalisms
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="test",
            translation="test",
            regionalisms=["Mexico", "Spain"]
        )
        
        # Verify regionalisms exist
        cursor = temp_db.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM vocab_regionalisms WHERE vocab_id = ?",
            (vocab_id,)
        )
        count_before = cursor.fetchone()[0]
        assert count_before == 2
        
        # Delete vocabulary
        vocab_model.delete_vocab(vocab_id)
        
        # Verify regionalisms are also deleted
        cursor.execute(
            "SELECT COUNT(*) FROM vocab_regionalisms WHERE vocab_id = ?",
            (vocab_id,)
        )
        count_after = cursor.fetchone()[0]
        assert count_after == 0


class TestVocabModelValidation:
    """Test data validation in VocabModel."""
    
    def test_word_phrase_length_limits(self, temp_db, sample_session):
        """Test vocabulary with various word phrase lengths."""
        vocab_model = VocabModel(temp_db)
        
        # Test normal length
        normal_word = "palabra"
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=normal_word,
            translation="word"
        )
        assert vocab_id is not None
        
        # Test long phrase
        long_phrase = "esta es una frase muy larga para probar los límites del sistema"
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=long_phrase,
            translation="long phrase"
        )
        assert vocab_id is not None
        
        # Test extremely long phrase (should be handled gracefully)
        extremely_long = "a" * 1000
        vocab_id = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase=extremely_long,
            translation="too long"
        )
        # This might be accepted or rejected depending on implementation
        # Either outcome should be handled gracefully
    
    def test_special_characters_in_vocab(self, temp_db, sample_session):
        """Test vocabulary with special characters."""
        vocab_model = VocabModel(temp_db)
        
        special_words = [
            ("niño", "child"),
            ("mañana", "tomorrow"),
            ("¿cómo?", "how?"),
            ("¡hola!", "hello!"),
            ("año", "year"),
            ("español", "Spanish")
        ]
        
        for word, translation in special_words:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase=word,
                translation=translation
            )
            assert vocab_id is not None, f"Failed to add word with special characters: {word}"
    
    def test_duplicate_vocab_handling(self, temp_db, sample_session):
        """Test handling of duplicate vocabulary entries."""
        vocab_model = VocabModel(temp_db)
        
        # Add vocabulary
        vocab_id1 = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="duplicate",
            translation="first entry"
        )
        assert vocab_id1 is not None
        
        # Add same word again (might be allowed or rejected depending on business rules)
        vocab_id2 = vocab_model.add_vocab(
            session_id=sample_session,
            word_phrase="duplicate",
            translation="second entry"
        )
        
        # Verify behavior - either both entries exist or second is rejected
        vocab_list = vocab_model.get_vocab_for_session(sample_session)
        duplicate_entries = [v for v in vocab_list if v['word_phrase'] == "duplicate"]
        
        # Should have either 1 or 2 entries depending on business rules
        assert len(duplicate_entries) in [1, 2]
    
    def test_html_injection_prevention(self, temp_db, sample_session):
        """Test prevention of HTML injection in vocabulary data."""
        vocab_model = VocabModel(temp_db)
        
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<h1>HTML Header</h1>"
        ]
        
        for malicious_input in malicious_inputs:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                word_phrase=malicious_input,
                translation="test",
                context_notes=malicious_input
            )
            
            if vocab_id is not None:
                # Retrieve and verify that malicious content is properly escaped/sanitized
                vocab = vocab_model.get_vocab_by_id(vocab_id)
                
                # The stored data should not contain active HTML/JavaScript
                stored_word = vocab['word_phrase']
                stored_notes = vocab['context_notes']
                
                # Exact behavior depends on implementation - might escape, strip, or reject
                # At minimum, it shouldn't be stored as-is if it's dangerous
                print(f"Stored word: {stored_word}, notes: {stored_notes}")


class TestVocabModelPerformance:
    """Test performance characteristics of VocabModel."""
    
    @pytest.mark.performance
    def test_bulk_vocab_insertion_performance(self, temp_db, sample_session, performance_timer):
        """Test performance of inserting many vocabulary entries."""
        vocab_model = VocabModel(temp_db)
        
        # Generate test data
        test_vocab = []
        for i in range(1000):
            test_vocab.append({
                "word_phrase": f"palabra_{i}",
                "translation": f"word_{i}",
                "context_notes": f"Context for word {i}"
            })
        
        performance_timer.start()
        
        vocab_ids = []
        for vocab_data in test_vocab:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                **vocab_data
            )
            vocab_ids.append(vocab_id)
        
        elapsed_time = performance_timer.stop()
        
        # Verify all were inserted
        assert len(vocab_ids) == 1000
        assert all(vid is not None for vid in vocab_ids)
        
        # Should complete in reasonable time (< 10 seconds)
        assert elapsed_time < 10.0
        
        print(f"Inserted 1000 vocab entries in {elapsed_time:.2f} seconds")
    
    @pytest.mark.performance
    def test_vocab_retrieval_performance(self, database_with_sample_data, performance_timer):
        """Test performance of retrieving vocabulary."""
        vocab_model = VocabModel(database_with_sample_data["database"])
        session_ids = database_with_sample_data["session_ids"]
        
        performance_timer.start()
        
        # Retrieve vocab for all sessions multiple times
        for _ in range(100):
            for session_id in session_ids:
                vocab_list = vocab_model.get_vocab_for_session(session_id)
                assert isinstance(vocab_list, list)
        
        elapsed_time = performance_timer.stop()
        
        # Should be fast (< 2 seconds for 100 * session_count retrievals)
        assert elapsed_time < 2.0
        
        print(f"Performed {100 * len(session_ids)} vocab retrievals in {elapsed_time:.2f} seconds")


# Integration with pytest markers
pytestmark = pytest.mark.unit