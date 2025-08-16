# File: utils/export.py
import csv
import json
from datetime import datetime
from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel
from utils.logger import get_logger

logger = get_logger(__name__)

class DataExporter:
    """Simple data export functionality"""
    
    def __init__(self, db: Database):
        self.db = db
        self.session_model = SessionModel(db)
        self.vocab_model = VocabModel(db)
    
    def export_sessions_csv(self, filepath: str) -> bool:
        """Export all sessions to CSV"""
        try:
            sessions = self.session_model.get_sessions()
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Session ID', 'Teacher ID', 'Date', 'Start Time', 'Duration', 'Status'])
                
                for session in sessions:
                    writer.writerow([
                        session['session_id'],
                        session['teacher_id'], 
                        session['session_date'],
                        session['start_time'],
                        session['duration'],
                        session['status']
                    ])
            
            logger.info(f"Exported {len(sessions)} sessions to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export sessions: {e}")
            return False
    
    def export_vocab_csv(self, filepath: str, session_id: int = None) -> bool:
        """Export vocabulary to CSV (all or for specific session)"""
        try:
            if session_id:
                vocab_items = self.vocab_model.get_vocab_for_session(session_id)
            else:
                # Get all vocab across all sessions
                cursor = self.db.conn.cursor()
                cursor.execute("""
                    SELECT v.*, GROUP_CONCAT(r.country_name, ',') as countries
                    FROM vocab v
                    LEFT JOIN vocab_regionalisms r ON v.vocab_id = r.vocab_id
                    GROUP BY v.vocab_id
                    ORDER BY v.vocab_id
                """)
                vocab_items = cursor.fetchall()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Vocab ID', 'Session ID', 'Word/Phrase', 'Translation', 'Context', 'Countries'])
                
                for vocab in vocab_items:
                    writer.writerow([
                        vocab['vocab_id'],
                        vocab['session_id'],
                        vocab['word_phrase'],
                        vocab['translation'],
                        vocab['context_notes'],
                        vocab['countries'] or ''
                    ])
            
            logger.info(f"Exported {len(vocab_items)} vocab items to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export vocab: {e}")
            return False
    
    def export_all_json(self, filepath: str) -> bool:
        """Export all data to JSON format"""
        try:
            sessions = self.session_model.get_sessions()
            
            # Convert Row objects to dicts and get vocab for each session
            data = {
                "export_date": datetime.now().isoformat(),
                "sessions": []
            }
            
            for session in sessions:
                session_dict = dict(session)
                session_dict['vocabulary'] = [dict(v) for v in self.vocab_model.get_vocab_for_session(session['session_id'])]
                data["sessions"].append(session_dict)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported all data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return False