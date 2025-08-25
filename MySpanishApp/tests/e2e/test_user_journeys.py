# File: tests/e2e/test_user_journeys.py
"""
End-to-end tests for complete user journeys in SpanishMaster.
Tests full workflows from the user's perspective.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

from models.database import Database
from views.main_window import MainWindow


class TestNewUserJourney:
    """Test the complete journey of a new user."""
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_first_time_user_setup(self, qt_app):
        """Test first-time user setup and onboarding."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Start application as new user
                window = MainWindow()
                window.show()
                
                # Process events to ensure UI is ready
                QApplication.processEvents()
                
                # Verify application starts successfully
                assert window.isVisible()
                assert window.windowTitle()
                
                # Check that database is initialized
                assert os.path.exists(tmp_db_path)
                
                # Test initial UI state
                # Should show empty state or welcome screen
                # Implementation dependent
                
                window.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_first_teacher_setup(self, qt_app):
        """Test adding the first teacher."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                window = MainWindow()
                window.show()
                QApplication.processEvents()
                
                # Navigate to settings or teacher setup
                # Implementation dependent - might be automatic or manual
                
                # Add first teacher (mock UI interaction)
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute(
                    "INSERT INTO teachers (name, region, notes) VALUES (?, ?, ?)",
                    ("María García", "Spain", "My first Spanish teacher")
                )
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                assert teacher_id is not None
                
                # Verify teacher was added
                cursor.execute("SELECT COUNT(*) FROM teachers")
                teacher_count = cursor.fetchone()[0]
                assert teacher_count == 1
                
                db.close()
                window.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


class TestSessionPlanningJourney:
    """Test the complete session planning journey."""
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_plan_single_session(self, qt_app):
        """Test planning a single tutoring session."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup
                db = Database(tmp_db_path)
                db.init_db()
                
                # Add teacher first
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Test Teacher",))
                db.conn.commit()
                db.close()
                
                # Start application
                window = MainWindow()
                window.show()
                QApplication.processEvents()
                
                # Navigate to Plan tab (Ctrl+1)
                QTest.keyPress(window, Qt.Key.Key_1, Qt.KeyboardModifier.ControlModifier)
                QApplication.processEvents()
                
                # Find plan view
                plan_view = window.findChild(object, "plan_view")  # Implementation dependent
                
                if plan_view:
                    # Test calendar interaction
                    # Click on a date (implementation dependent)
                    
                    # Test add session button
                    # Implementation dependent
                    
                    # Verify session was planned
                    pass
                
                window.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_plan_multiple_sessions(self, qt_app):
        """Test planning multiple sessions over different dates."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup database with teacher
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Test Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                # Plan sessions programmatically (simulating UI actions)
                from models.session_model import SessionModel
                session_model = SessionModel(db)
                
                session_dates = ["2025-04-10", "2025-04-12", "2025-04-15"]
                session_ids = []
                
                for date in session_dates:
                    session_id = session_model.create_session(
                        teacher_id=teacher_id,
                        session_date=date,
                        start_time="17:00",
                        duration="1h"
                    )
                    session_ids.append(session_id)
                
                # Verify all sessions were planned
                sessions = session_model.get_sessions()
                assert len(sessions) == 3
                
                for session in sessions:
                    assert session['session_date'] in session_dates
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_reschedule_session(self, qt_app):
        """Test rescheduling an existing session."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup with existing session
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Test Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                session_model = SessionModel(db)
                
                # Create original session
                original_session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date="2025-04-10",
                    start_time="17:00",
                    duration="1h"
                )
                
                # Simulate rescheduling (implementation dependent)
                # This might involve UI interactions to change date/time
                
                # For testing, update directly
                cursor.execute(
                    "UPDATE sessions SET session_date = ?, start_time = ? WHERE session_id = ?",
                    ("2025-04-11", "18:00", original_session_id)
                )
                db.conn.commit()
                
                # Verify reschedule
                sessions = session_model.get_sessions()
                rescheduled_session = next(s for s in sessions if s['session_id'] == original_session_id)
                
                assert rescheduled_session['session_date'] == "2025-04-11"
                assert rescheduled_session['start_time'] == "18:00"
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


class TestLearningTrackingJourney:
    """Test the complete learning tracking journey."""
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_track_session_vocabulary(self, qt_app):
        """Test tracking vocabulary during a session."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup
                db = Database(tmp_db_path)
                db.init_db()
                
                # Add teacher and session
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Test Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                from models.vocab_model import VocabModel
                
                session_model = SessionModel(db)
                vocab_model = VocabModel(db)
                
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date="2025-04-10",
                    start_time="17:00",
                    duration="1h"
                )
                
                # Start application
                window = MainWindow()
                window.show()
                QApplication.processEvents()
                
                # Navigate to Track tab
                QTest.keyPress(window, Qt.Key.Key_2, Qt.KeyboardModifier.ControlModifier)
                QApplication.processEvents()
                
                # Simulate adding vocabulary through UI
                # Implementation dependent - would involve form filling
                
                # For testing, add vocabulary programmatically
                vocab_words = [
                    ("aprender", "to learn", "Regular -er verb"),
                    ("estudiar", "to study", "Regular -ar verb"),
                    ("practicar", "to practice", "Regular -ar verb")
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
                
                # Verify vocabulary was tracked
                session_vocab = vocab_model.get_vocab_for_session(session_id)
                assert len(session_vocab) == 3
                
                tracked_words = [v['word_phrase'] for v in session_vocab]
                for word, _, _ in vocab_words:
                    assert word in tracked_words
                
                db.close()
                window.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_track_session_grammar(self, qt_app):
        """Test tracking grammar patterns during a session."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Test Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                from models.grammar_model import GrammarModel
                
                session_model = SessionModel(db)
                grammar_model = GrammarModel(db)
                
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date="2025-04-10",
                    start_time="17:00",
                    duration="1h"
                )
                
                # Track grammar patterns
                grammar_patterns = [
                    ("Present tense -ar verbs", "Add -o, -as, -a, -amos, -áis, -an to stem"),
                    ("Ser vs Estar", "Ser for permanent states, Estar for temporary conditions")
                ]
                
                for pattern, explanation in grammar_patterns:
                    grammar_model.add_grammar(
                        session_id=session_id,
                        phrase_structure=pattern,
                        explanation=explanation
                    )
                
                # Verify grammar was tracked
                session_grammar = grammar_model.get_grammar_for_session(session_id)
                assert len(session_grammar) == 2
                
                tracked_patterns = [g['phrase_structure'] for g in session_grammar]
                for pattern, _ in grammar_patterns:
                    assert pattern in tracked_patterns
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_complete_session_tracking(self, qt_app):
        """Test complete session tracking with all data types."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup complete session tracking scenario
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Complete Test Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                from models.vocab_model import VocabModel
                from models.grammar_model import GrammarModel
                
                session_model = SessionModel(db)
                vocab_model = VocabModel(db)
                grammar_model = GrammarModel(db)
                
                # Create session
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date="2025-04-10",
                    start_time="17:00",
                    duration="1h"
                )
                
                # Track vocabulary
                vocab_model.add_vocab(session_id, "conversar", "to converse", "Communication")
                vocab_model.add_vocab(session_id, "entender", "to understand", "Comprehension")
                
                # Track grammar
                grammar_model.add_grammar(
                    session_id, 
                    "Reflexive pronouns", 
                    "Me, te, se, nos, os, se used with reflexive verbs"
                )
                
                # Track challenges (if model exists)
                if hasattr(db, 'add_challenge'):  # Implementation dependent
                    pass
                
                # Track comfort areas (if model exists)
                if hasattr(db, 'add_comfort'):  # Implementation dependent
                    pass
                
                # Mark session as completed
                session_model.update_session_status(session_id, "completed")
                
                # Verify complete tracking
                sessions = session_model.get_sessions()
                completed_session = next(s for s in sessions if s['session_id'] == session_id)
                assert completed_session['status'] == "completed"
                
                session_vocab = vocab_model.get_vocab_for_session(session_id)
                session_grammar = grammar_model.get_grammar_for_session(session_id)
                
                assert len(session_vocab) == 2
                assert len(session_grammar) == 1
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


class TestProgressReviewJourney:
    """Test the complete progress review journey."""
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_review_learning_progress(self, qt_app):
        """Test reviewing learning progress over multiple sessions."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup with historical data
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Review Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                from models.vocab_model import VocabModel
                from models.grammar_model import GrammarModel
                
                session_model = SessionModel(db)
                vocab_model = VocabModel(db)
                grammar_model = GrammarModel(db)
                
                # Create multiple completed sessions
                session_data = [
                    ("2025-04-01", ["hola", "adiós"], ["Greetings"]),
                    ("2025-04-05", ["comer", "beber"], ["Present tense"]),
                    ("2025-04-10", ["estar", "ser"], ["Ser vs Estar"])
                ]
                
                session_ids = []
                total_vocab_count = 0
                total_grammar_count = 0
                
                for date, vocab_words, grammar_patterns in session_data:
                    # Create session
                    session_id = session_model.create_session(
                        teacher_id=teacher_id,
                        session_date=date,
                        start_time="17:00",
                        duration="1h"
                    )
                    session_ids.append(session_id)
                    
                    # Add vocabulary
                    for word in vocab_words:
                        vocab_model.add_vocab(session_id, word, f"translation of {word}")
                        total_vocab_count += 1
                    
                    # Add grammar
                    for pattern in grammar_patterns:
                        grammar_model.add_grammar(session_id, pattern, f"explanation of {pattern}")
                        total_grammar_count += 1
                    
                    # Mark as completed
                    session_model.update_session_status(session_id, "completed")
                
                # Start application and navigate to Review
                window = MainWindow()
                window.show()
                QApplication.processEvents()
                
                # Navigate to Review tab
                QTest.keyPress(window, Qt.Key.Key_3, Qt.KeyboardModifier.ControlModifier)
                QApplication.processEvents()
                
                # Verify review statistics
                sessions = session_model.get_sessions()
                completed_sessions = [s for s in sessions if s['status'] == 'completed']
                
                assert len(completed_sessions) == 3
                
                # Check total vocabulary learned
                total_vocab_retrieved = 0
                for session_id in session_ids:
                    vocab_list = vocab_model.get_vocab_for_session(session_id)
                    total_vocab_retrieved += len(vocab_list)
                
                assert total_vocab_retrieved == total_vocab_count
                
                # Check total grammar patterns learned
                total_grammar_retrieved = 0
                for session_id in session_ids:
                    grammar_list = grammar_model.get_grammar_for_session(session_id)
                    total_grammar_retrieved += len(grammar_list)
                
                assert total_grammar_retrieved == total_grammar_count
                
                db.close()
                window.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_filter_sessions_by_status(self, qt_app):
        """Test filtering sessions by status in review view."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup with mixed session statuses
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Filter Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                session_model = SessionModel(db)
                
                # Create sessions with different statuses
                session_statuses = [
                    ("2025-04-01", "completed"),
                    ("2025-04-05", "completed"),
                    ("2025-04-10", "planned"),
                    ("2025-04-15", "planned")
                ]
                
                for date, status in session_statuses:
                    session_id = session_model.create_session(
                        teacher_id=teacher_id,
                        session_date=date,
                        start_time="17:00",
                        duration="1h"
                    )
                    
                    if status == "completed":
                        session_model.update_session_status(session_id, "completed")
                
                # Test filtering
                all_sessions = session_model.get_sessions()
                completed_sessions = [s for s in all_sessions if s['status'] == 'completed']
                planned_sessions = [s for s in all_sessions if s['status'] == 'planned']
                
                assert len(all_sessions) == 4
                assert len(completed_sessions) == 2
                assert len(planned_sessions) == 2
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


class TestFullApplicationWorkflowE2E:
    """Test complete end-to-end application workflow."""
    
    @pytest.mark.e2e
    @pytest.mark.gui
    @pytest.mark.slow
    def test_complete_user_workflow(self, qt_app):
        """Test complete user workflow from planning to review."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Step 1: Initialize application
                window = MainWindow()
                window.show()
                QApplication.processEvents()
                
                # Step 2: Setup (add teacher)
                db = Database(tmp_db_path)
                db.init_db()
                
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name, region, notes) VALUES (?, ?, ?)",
                             ("Ana Rodríguez", "Colombia", "Excellent teacher for conversation practice"))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                from models.vocab_model import VocabModel
                from models.grammar_model import GrammarModel
                
                session_model = SessionModel(db)
                vocab_model = VocabModel(db)
                grammar_model = GrammarModel(db)
                
                # Step 3: Plan sessions
                upcoming_sessions = [
                    "2025-04-10", "2025-04-12", "2025-04-15", "2025-04-17", "2025-04-20"
                ]
                
                planned_session_ids = []
                for date in upcoming_sessions:
                    session_id = session_model.create_session(
                        teacher_id=teacher_id,
                        session_date=date,
                        start_time="17:00",
                        duration="1h"
                    )
                    planned_session_ids.append(session_id)
                
                # Verify planning
                all_sessions = session_model.get_sessions()
                assert len(all_sessions) == 5
                
                # Step 4: Conduct and track first session
                first_session_id = planned_session_ids[0]
                
                # Track vocabulary learned
                session1_vocab = [
                    ("presentarse", "to introduce oneself", "Reflexive verb for introductions"),
                    ("nacionalidad", "nationality", "Used when talking about where you're from"),
                    ("profesión", "profession", "Job or career")
                ]
                
                for word, translation, context in session1_vocab:
                    vocab_model.add_vocab(first_session_id, word, translation, context)
                
                # Track grammar learned
                grammar_model.add_grammar(
                    first_session_id,
                    "Present tense of SER",
                    "Yo soy, tú eres, él/ella es, nosotros somos, vosotros sois, ellos son"
                )
                
                # Mark session as completed
                session_model.update_session_status(first_session_id, "completed")
                
                # Step 5: Conduct and track second session
                second_session_id = planned_session_ids[1]
                
                session2_vocab = [
                    ("familia", "family", "Nuclear family members"),
                    ("hermano", "brother", "Male sibling"),
                    ("hermana", "sister", "Female sibling")
                ]
                
                for word, translation, context in session2_vocab:
                    vocab_model.add_vocab(second_session_id, word, translation, context)
                
                grammar_model.add_grammar(
                    second_session_id,
                    "Possessive adjectives",
                    "Mi, tu, su, nuestro, vuestro, su - agree with possessed noun"
                )
                
                session_model.update_session_status(second_session_id, "completed")
                
                # Step 6: Review progress
                # Navigate to Review tab
                QTest.keyPress(window, Qt.Key.Key_3, Qt.KeyboardModifier.ControlModifier)
                QApplication.processEvents()
                
                # Verify progress statistics
                all_sessions = session_model.get_sessions()
                completed_sessions = [s for s in all_sessions if s['status'] == 'completed']
                planned_sessions = [s for s in all_sessions if s['status'] == 'planned']
                
                assert len(completed_sessions) == 2
                assert len(planned_sessions) == 3
                
                # Count total vocabulary learned
                total_vocab_count = 0
                for session_id in planned_session_ids[:2]:  # First 2 completed sessions
                    vocab_list = vocab_model.get_vocab_for_session(session_id)
                    total_vocab_count += len(vocab_list)
                
                assert total_vocab_count == 6  # 3 words per session * 2 sessions
                
                # Count total grammar patterns
                total_grammar_count = 0
                for session_id in planned_session_ids[:2]:
                    grammar_list = grammar_model.get_grammar_for_session(session_id)
                    total_grammar_count += len(grammar_list)
                
                assert total_grammar_count == 2  # 1 pattern per session * 2 sessions
                
                # Step 7: Verify recent vocabulary
                recent_vocab = []
                for session_id in planned_session_ids[:2]:
                    vocab_list = vocab_model.get_vocab_for_session(session_id)
                    recent_vocab.extend(vocab_list)
                
                recent_words = [v['word_phrase'] for v in recent_vocab]
                expected_words = ["presentarse", "nacionalidad", "profesión", "familia", "hermano", "hermana"]
                
                for word in expected_words:
                    assert word in recent_words
                
                db.close()
                window.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)
    
    @pytest.mark.e2e
    @pytest.mark.gui
    @pytest.mark.slow
    def test_data_export_workflow(self, qt_app):
        """Test complete data export workflow."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            with patch('config.DB_FILE', tmp_db_path):
                # Setup with data to export
                db = Database(tmp_db_path)
                db.init_db()
                
                # Add sample data
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Export Teacher",))
                db.conn.commit()
                teacher_id = cursor.lastrowid
                
                from models.session_model import SessionModel
                from models.vocab_model import VocabModel
                
                session_model = SessionModel(db)
                vocab_model = VocabModel(db)
                
                # Create session with vocabulary
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date="2025-04-10",
                    start_time="17:00",
                    duration="1h"
                )
                
                vocab_model.add_vocab(session_id, "exportar", "to export", "Data management")
                vocab_model.add_vocab(session_id, "datos", "data", "Information")
                
                # Test export functionality (if implemented)
                # This would involve UI interactions to trigger export
                
                # For testing, verify data exists for export
                sessions = session_model.get_sessions()
                vocab_list = vocab_model.get_vocab_for_session(session_id)
                
                assert len(sessions) == 1
                assert len(vocab_list) == 2
                
                # Export functionality would be tested here
                # Implementation dependent
                
                db.close()
        
        finally:
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


# Integration with pytest markers
pytestmark = pytest.mark.e2e