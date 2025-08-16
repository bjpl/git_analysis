# File: tests/test_models.py
import os
import tempfile
import pytest
from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel

@pytest.fixture
def test_db():
    """Create a temporary test database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db = Database(tmp.name)
        db.init_db()
        yield db
        db.close()
        os.unlink(tmp.name)

def test_create_session(test_db):
    """Test session creation with valid data"""
    session_model = SessionModel(test_db)
    session_id = session_model.create_session(
        teacher_id=1,
        session_date="2025-04-10",
        start_time="17:00",
        duration="1h"
    )
    assert session_id is not None

def test_create_session_missing_data(test_db):
    """Test session creation with missing required data"""
    session_model = SessionModel(test_db)
    session_id = session_model.create_session(
        teacher_id=None,
        session_date="2025-04-10",
        start_time="17:00",
        duration="1h"
    )
    assert session_id is None

def test_add_vocab(test_db):
    """Test adding vocabulary with valid data"""
    session_model = SessionModel(test_db)
    vocab_model = VocabModel(test_db)
    
    session_id = session_model.create_session(1, "2025-04-10", "17:00", "1h")
    vocab_id = vocab_model.add_vocab(
        session_id=session_id,
        word_phrase="faltar",
        translation="to be missing"
    )
    assert vocab_id is not None

def test_add_vocab_missing_data(test_db):
    """Test adding vocabulary with missing required data"""
    vocab_model = VocabModel(test_db)
    vocab_id = vocab_model.add_vocab(
        session_id=None,
        word_phrase="faltar"
    )
    assert vocab_id is None

def test_session_status_update(test_db):
    """Test updating session status"""
    session_model = SessionModel(test_db)
    session_id = session_model.create_session(1, "2025-04-10", "17:00", "1h")
    
    # Update status
    result = session_model.update_session_status(session_id, "completed")
    assert result > 0  # Should affect 1 row

def test_vocab_deletion(test_db):
    """Test vocabulary deletion"""
    session_model = SessionModel(test_db)
    vocab_model = VocabModel(test_db)
    
    session_id = session_model.create_session(1, "2025-04-10", "17:00", "1h")
    vocab_id = vocab_model.add_vocab(session_id, "test_word", "test translation")
    
    # Delete vocab
    result = vocab_model.delete_vocab(vocab_id)
    assert result > 0  # Should affect 1 row

def test_db_models():
    db = Database()       # Connect & create the DB file if not present
    db.init_db()          # Create tables if not exist

    session_model = SessionModel(db)
    vocab_model = VocabModel(db)

    # 1. Create a test teacher (optional) or assume teacher_id=1 if you inserted manually
    # For a quick test, let's assume teacher_id=1. 
    # Ideally, you'd have a teacher_model to create a teacher row.

    # 2. Create a session
    test_session_id = session_model.create_session(
        teacher_id=1,
        session_date="2025-04-10",
        start_time="17:00",
        duration="1h"
    )

    # 3. Add some vocab
    if test_session_id:
        vocab_model.add_vocab(
            session_id=test_session_id,
            word_phrase="faltar",
            translation="to be missing",
            context_notes="Used in expression 'me falta'",
            regionalisms=["Mexico", "Argentina"]
        )

    # 4. Read back the sessions
    all_sessions = session_model.get_sessions()
    for s in all_sessions:
        print(f"Session ID={s['session_id']}, teacher_id={s['teacher_id']}, date={s['session_date']}")

    # 5. Read back vocab
    if test_session_id:
        vocab_list = vocab_model.get_vocab_for_session(test_session_id)
        for v in vocab_list:
            print(f"Vocab ID={v['vocab_id']}, word={v['word_phrase']}, countries={v['countries']}")

    # Clean up
    db.close()

if __name__ == "__main__":
    test_db_models()