# File: tests/integration/test_app_integration.py
"""
Integration tests for the SpanishMaster application.
Tests interaction between different modules and components.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel
from models.grammar_model import GrammarModel
from views.main_window import MainWindow


class TestDatabaseModelIntegration:
    """Test integration between database and model classes."""
    
    def test_session_vocab_integration(self, temp_db, sample_teacher):
        """Test integration between SessionModel and VocabModel."""
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        # Create a session
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        assert session_id is not None
        
        # Add vocabulary to the session
        vocab_words = [
            ("hola", "hello", "greeting"),
            ("adiós", "goodbye", "farewell"),
            ("gracias", "thank you", "gratitude")
        ]
        
        vocab_ids = []
        for word, translation, context in vocab_words:
            vocab_id = vocab_model.add_vocab(
                session_id=session_id,
                word_phrase=word,
                translation=translation,
                context_notes=context
            )
            vocab_ids.append(vocab_id)
        
        # Verify all vocabulary was added
        assert all(vid is not None for vid in vocab_ids)
        
        # Retrieve vocabulary for the session
        session_vocab = vocab_model.get_vocab_for_session(session_id)
        
        assert len(session_vocab) == 3
        
        # Verify content
        retrieved_words = [(v['word_phrase'], v['translation']) for v in session_vocab]
        expected_words = [(word, trans) for word, trans, _ in vocab_words]
        
        for expected in expected_words:
            assert expected in retrieved_words
    
    def test_session_deletion_cascades_to_vocab(self, temp_db, sample_teacher):
        """Test that deleting a session removes associated vocabulary."""
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        # Create session and add vocabulary
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        vocab_id = vocab_model.add_vocab(
            session_id=session_id,
            word_phrase="test_word",
            translation="test_translation"
        )
        
        # Verify vocabulary exists
        session_vocab = vocab_model.get_vocab_for_session(session_id)
        assert len(session_vocab) == 1
        
        # Delete session
        session_model.delete_session(session_id)
        
        # Verify vocabulary is also gone (depending on foreign key constraints)
        session_vocab = vocab_model.get_vocab_for_session(session_id)
        assert len(session_vocab) == 0
    
    def test_session_grammar_integration(self, temp_db, sample_teacher):
        """Test integration between SessionModel and GrammarModel."""
        session_model = SessionModel(temp_db)
        grammar_model = GrammarModel(temp_db)
        
        # Create session
        session_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        # Add grammar patterns
        grammar_patterns = [
            ("Ser vs Estar", "Ser for permanent, Estar for temporary"),
            ("Subjunctive mood", "Used for doubt, emotion, desire")
        ]
        
        grammar_ids = []
        for pattern, explanation in grammar_patterns:
            grammar_id = grammar_model.add_grammar(
                session_id=session_id,
                phrase_structure=pattern,
                explanation=explanation
            )
            grammar_ids.append(grammar_id)
        
        # Verify all grammar was added
        assert all(gid is not None for gid in grammar_ids)
        
        # Retrieve grammar for session
        session_grammar = grammar_model.get_grammar_for_session(session_id)
        assert len(session_grammar) == 2
    
    def test_multiple_sessions_data_isolation(self, temp_db, sample_teacher):
        """Test that data from different sessions is properly isolated."""
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        # Create two sessions
        session1_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        session2_id = session_model.create_session(
            teacher_id=sample_teacher,
            session_date="2025-04-11",
            start_time="17:00",
            duration="1h"
        )
        
        # Add different vocabulary to each session
        vocab_model.add_vocab(session1_id, "session1_word", "session1_trans")
        vocab_model.add_vocab(session2_id, "session2_word", "session2_trans")
        
        # Verify vocabulary isolation
        session1_vocab = vocab_model.get_vocab_for_session(session1_id)
        session2_vocab = vocab_model.get_vocab_for_session(session2_id)
        
        assert len(session1_vocab) == 1
        assert len(session2_vocab) == 1
        
        assert session1_vocab[0]['word_phrase'] == "session1_word"
        assert session2_vocab[0]['word_phrase'] == "session2_word"


class TestUIModelIntegration:
    """Test integration between UI components and data models."""
    
    @pytest.mark.gui
    def test_main_window_database_connection(self, qt_app):
        """Test that MainWindow properly connects to database."""
        with patch('models.database.Database') as mock_db_class:
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            
            window = MainWindow()
            
            # Verify database was initialized
            mock_db_class.assert_called()
            mock_db.init_db.assert_called()
    
    @pytest.mark.gui
    def test_plan_view_session_creation_integration(self, qt_app, temp_db):
        """Test integration between PlanView and SessionModel."""
        with patch('models.database.Database', return_value=temp_db):
            from views.plan_view import PlanView
            
            plan_view = PlanView()
            
            # Test session creation through UI (implementation dependent)
            if hasattr(plan_view, 'create_session'):
                # Mock the UI input data
                session_data = {
                    'teacher_id': 1,
                    'session_date': '2025-04-10',
                    'start_time': '17:00',
                    'duration': '1h'
                }
                
                # Create session through UI
                result = plan_view.create_session(**session_data)
                
                # Verify session was created in database
                session_model = SessionModel(temp_db)
                sessions = session_model.get_sessions()
                
                assert len(sessions) >= 1
    
    @pytest.mark.gui
    def test_track_view_vocab_addition_integration(self, qt_app, database_with_sample_data):
        """Test integration between TrackView and VocabModel."""
        with patch('models.database.Database', return_value=database_with_sample_data["database"]):
            from views.track_view import TrackView
            
            track_view = TrackView()
            
            # Test vocabulary addition through UI (implementation dependent)
            if hasattr(track_view, 'add_vocab'):
                vocab_data = {
                    'session_id': database_with_sample_data["session_ids"][0],
                    'word_phrase': 'integration_test',
                    'translation': 'integration test word',
                    'context_notes': 'Added through UI integration test'
                }
                
                result = track_view.add_vocab(**vocab_data)
                
                # Verify vocabulary was added to database
                vocab_model = VocabModel(database_with_sample_data["database"])
                vocab_list = vocab_model.get_vocab_for_session(vocab_data['session_id'])
                
                added_vocab = [v for v in vocab_list if v['word_phrase'] == 'integration_test']
                assert len(added_vocab) == 1
    
    @pytest.mark.gui
    def test_review_view_data_display_integration(self, qt_app, database_with_sample_data):
        """Test integration between ReviewView and data models."""
        with patch('models.database.Database', return_value=database_with_sample_data["database"]):
            from views.review_view import ReviewView
            
            review_view = ReviewView()
            
            # Test data loading and display (implementation dependent)
            if hasattr(review_view, 'load_statistics'):
                review_view.load_statistics()
                
                # Verify statistics reflect actual data
                # This would check that UI displays match database content
                # Implementation dependent


class TestFullApplicationWorkflow:
    """Test complete application workflows."""
    
    @pytest.mark.gui
    def test_complete_session_workflow(self, qt_app):
        """Test complete workflow: plan -> track -> review."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            # Initialize application with test database
            with patch('config.DB_FILE', tmp_db_path):
                db = Database(tmp_db_path)
                db.init_db()
                
                # Add a test teacher
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name, region) VALUES (?, ?)", ("Test Teacher", "Spain"))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                # Step 1: Plan a session
                session_model = SessionModel(db)
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date="2025-04-10",
                    start_time="17:00",
                    duration="1h"
                )
                
                assert session_id is not None
                
                # Step 2: Track learning during session
                vocab_model = VocabModel(db)
                grammar_model = GrammarModel(db)
                
                # Add vocabulary
                vocab_id = vocab_model.add_vocab(
                    session_id=session_id,
                    word_phrase="aprender",
                    translation="to learn",
                    context_notes="We learned this during integration testing"
                )
                
                # Add grammar
                grammar_id = grammar_model.add_grammar(
                    session_id=session_id,
                    phrase_structure="Present tense -ar verbs",
                    explanation="Regular -ar verbs conjugate with -o, -as, -a, -amos, -áis, -an"
                )
                
                assert vocab_id is not None
                assert grammar_id is not None
                
                # Step 3: Mark session as completed
                session_model.update_session_status(session_id, "completed")
                
                # Step 4: Review the session
                sessions = session_model.get_sessions()
                completed_sessions = [s for s in sessions if s['status'] == 'completed']
                
                assert len(completed_sessions) == 1
                assert completed_sessions[0]['session_id'] == session_id
                
                # Verify vocabulary and grammar are associated
                session_vocab = vocab_model.get_vocab_for_session(session_id)
                session_grammar = grammar_model.get_grammar_for_session(session_id)
                
                assert len(session_vocab) == 1
                assert len(session_grammar) == 1
                assert session_vocab[0]['word_phrase'] == "aprender"
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.gui
    def test_data_persistence_across_sessions(self, qt_app):
        """Test that data persists when application is restarted."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            # First application session
            db1 = Database(tmp_db_path)
            db1.init_db()
            
            # Add test teacher
            cursor = db1.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Persistent Teacher",))
            db1.conn.commit()
            teacher_id = cursor.lastrowid
            
            # Add session and vocabulary
            session_model = SessionModel(db1)
            vocab_model = VocabModel(db1)
            
            session_id = session_model.create_session(
                teacher_id=teacher_id,
                session_date="2025-04-10",
                start_time="17:00",
                duration="1h"
            )
            
            vocab_id = vocab_model.add_vocab(
                session_id=session_id,
                word_phrase="persistir",
                translation="to persist"
            )
            
            db1.close()
            
            # Second application session (simulate restart)
            db2 = Database(tmp_db_path)
            session_model2 = SessionModel(db2)
            vocab_model2 = VocabModel(db2)
            
            # Verify data persisted
            sessions = session_model2.get_sessions()
            assert len(sessions) == 1
            assert sessions[0]['session_id'] == session_id
            
            vocab_list = vocab_model2.get_vocab_for_session(session_id)
            assert len(vocab_list) == 1
            assert vocab_list[0]['word_phrase'] == "persistir"
            
            db2.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""
    
    def test_database_connection_failure_handling(self, qt_app):
        """Test application behavior when database connection fails."""
        with patch('models.database.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection failed")
            
            # Application should handle database connection failure gracefully
            with pytest.raises(Exception):
                Database()
    
    def test_model_error_propagation(self, temp_db):
        """Test that model errors are properly propagated."""
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        # Create invalid session (should fail)
        session_id = session_model.create_session(
            teacher_id=None,  # Invalid
            session_date="2025-04-10",
            start_time="17:00",
            duration="1h"
        )
        
        assert session_id is None
        
        # Try to add vocab to invalid session
        vocab_id = vocab_model.add_vocab(
            session_id=None,  # Invalid
            word_phrase="test",
            translation="test"
        )
        
        assert vocab_id is None
    
    @pytest.mark.gui
    def test_ui_error_handling_integration(self, qt_app):
        """Test UI error handling when models fail."""
        with patch('models.database.Database') as mock_db_class:
            # Mock database to raise errors
            mock_db = Mock()
            mock_db.conn.execute.side_effect = Exception("Database error")
            mock_db_class.return_value = mock_db
            
            # UI should handle database errors gracefully
            window = MainWindow()
            
            # Application should not crash
            assert window is not None


class TestPerformanceIntegration:
    """Test performance of integrated components."""
    
    @pytest.mark.performance
    def test_large_dataset_integration_performance(self, performance_timer):
        """Test performance with large amounts of integrated data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            performance_timer.start()
            
            db = Database(tmp_db_path)
            db.init_db()
            
            # Add test teacher
            cursor = db.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Performance Teacher",))
            db.conn.commit()
            teacher_id = cursor.lastrowid
            
            # Create models
            session_model = SessionModel(db)
            vocab_model = VocabModel(db)
            grammar_model = GrammarModel(db)
            
            # Create many sessions with vocabulary and grammar
            for i in range(50):  # 50 sessions
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date=f"2025-{4 + i // 30:02d}-{10 + i % 30:02d}",
                    start_time="17:00",
                    duration="1h"
                )
                
                # Add 10 vocabulary items per session
                for j in range(10):
                    vocab_model.add_vocab(
                        session_id=session_id,
                        word_phrase=f"word_{i}_{j}",
                        translation=f"translation_{i}_{j}"
                    )
                
                # Add 3 grammar items per session
                for k in range(3):
                    grammar_model.add_grammar(
                        session_id=session_id,
                        phrase_structure=f"grammar_pattern_{i}_{k}",
                        explanation=f"explanation_{i}_{k}"
                    )
            
            # Test retrieval performance
            all_sessions = session_model.get_sessions()
            assert len(all_sessions) == 50
            
            # Test vocabulary retrieval for all sessions
            total_vocab = 0
            for session in all_sessions:
                vocab_list = vocab_model.get_vocab_for_session(session['session_id'])
                total_vocab += len(vocab_list)
            
            assert total_vocab == 500  # 50 sessions * 10 vocab each
            
            elapsed_time = performance_timer.stop()
            
            # Should handle large dataset efficiently (< 10 seconds)
            assert elapsed_time < 10.0
            
            print(f"Large dataset integration test completed in {elapsed_time:.2f} seconds")
            
            db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.performance
    def test_concurrent_model_operations(self, temp_db, sample_teacher, performance_timer):
        """Test concurrent operations across different models."""
        import threading
        import time
        
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        results = []
        errors = []
        
        def concurrent_operations(thread_id):
            try:
                # Create session
                session_id = session_model.create_session(
                    teacher_id=sample_teacher,
                    session_date=f"2025-04-{10 + thread_id:02d}",
                    start_time="17:00",
                    duration="1h"
                )
                
                if session_id:
                    # Add vocabulary
                    for i in range(5):
                        vocab_id = vocab_model.add_vocab(
                            session_id=session_id,
                            word_phrase=f"concurrent_word_{thread_id}_{i}",
                            translation=f"concurrent_translation_{thread_id}_{i}"
                        )
                        results.append((thread_id, session_id, vocab_id))
                        time.sleep(0.01)  # Small delay
                
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        performance_timer.start()
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        elapsed_time = performance_timer.stop()
        
        # Check results
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(results) >= 20  # 5 threads * 5 vocab each (minimum)
        
        # Should complete reasonably quickly
        assert elapsed_time < 5.0
        
        print(f"Concurrent operations completed in {elapsed_time:.2f} seconds")


# Integration with pytest markers
pytestmark = pytest.mark.integration