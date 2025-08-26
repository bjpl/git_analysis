#!/usr/bin/env python3
"""
Core Questionnaire Functionality
Extracted from image-questionnaire-gpt project for simplified use with Tkinter

Key features:
1. Question/Answer dialog system
2. Session logging to CSV
3. Progress tracking
4. Settings management
"""

import os
import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class QuestionnaireSession:
    """Data class to track a questionnaire session"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    total_questions: int = 0
    answered_questions: int = 0
    responses: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.responses is None:
            self.responses = []


@dataclass
class QuestionResponse:
    """Data class for individual question responses"""
    question_id: int
    question_text: str
    answer: str
    timestamp: str
    processing_time_ms: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None


class SessionManager:
    """Manages questionnaire sessions and logging to CSV"""
    
    def __init__(self, log_directory: str = "sessions"):
        self.log_directory = log_directory
        self.current_session: Optional[QuestionnaireSession] = None
        
        # Ensure log directory exists BEFORE setting up logging
        os.makedirs(self.log_directory, exist_ok=True)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    os.path.join(self.log_directory, "questionnaire.log"), 
                    mode="a"
                )
            ]
        )
    
    def start_session(self, total_questions: int = 0) -> str:
        """Start a new questionnaire session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = QuestionnaireSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            total_questions=total_questions
        )
        
        logging.info(f"Started questionnaire session: {session_id}")
        return session_id
    
    def add_response(self, question_id: int, question_text: str, 
                    answer: str, processing_time_ms: Optional[int] = None,
                    additional_data: Optional[Dict[str, Any]] = None):
        """Add a response to the current session"""
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        response = QuestionResponse(
            question_id=question_id,
            question_text=question_text,
            answer=answer,
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time_ms,
            additional_data=additional_data
        )
        
        self.current_session.responses.append(asdict(response))
        self.current_session.answered_questions += 1
        
        logging.info(f"Added response for question {question_id}")
    
    def end_session(self) -> Optional[str]:
        """End the current session and save to CSV"""
        if not self.current_session:
            logging.warning("No active session to end")
            return None
        
        self.current_session.end_time = datetime.now().isoformat()
        
        # Save to CSV
        csv_path = self.save_session_to_csv()
        
        # Save to JSON as backup
        json_path = self.save_session_to_json()
        
        session_id = self.current_session.session_id
        self.current_session = None
        
        logging.info(f"Ended session {session_id}, saved to {csv_path}")
        return csv_path
    
    def save_session_to_csv(self) -> str:
        """Save current session to CSV file"""
        if not self.current_session:
            raise ValueError("No active session to save")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{self.current_session.session_id}_{timestamp}.csv"
        csv_path = os.path.join(self.log_directory, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Write session metadata first
            writer = csv.writer(csvfile)
            writer.writerow(['Session Metadata'])
            writer.writerow(['Session ID', self.current_session.session_id])
            writer.writerow(['Start Time', self.current_session.start_time])
            writer.writerow(['End Time', self.current_session.end_time])
            writer.writerow(['Total Questions', self.current_session.total_questions])
            writer.writerow(['Answered Questions', self.current_session.answered_questions])
            writer.writerow([])  # Empty row separator
            
            # Write responses
            if self.current_session.responses:
                writer.writerow(['Question Responses'])
                writer.writerow([
                    'Question ID', 'Question Text', 'Answer', 'Timestamp', 
                    'Processing Time (ms)', 'Additional Data'
                ])
                
                for response in self.current_session.responses:
                    additional_data_str = json.dumps(response.get('additional_data', {}))
                    writer.writerow([
                        response['question_id'],
                        response['question_text'],
                        response['answer'],
                        response['timestamp'],
                        response.get('processing_time_ms', ''),
                        additional_data_str
                    ])
        
        return csv_path
    
    def save_session_to_json(self) -> str:
        """Save current session to JSON file as backup"""
        if not self.current_session:
            raise ValueError("No active session to save")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{self.current_session.session_id}_{timestamp}.json"
        json_path = os.path.join(self.log_directory, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(asdict(self.current_session), jsonfile, indent=2, ensure_ascii=False)
        
        return json_path
    
    def get_progress(self) -> Tuple[int, int]:
        """Get current session progress (answered, total)"""
        if not self.current_session:
            return 0, 0
        return self.current_session.answered_questions, self.current_session.total_questions


class QuestionnaireSettings:
    """Manages questionnaire configuration settings"""
    
    def __init__(self, settings_file: str = "questionnaire_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "session_directory": "sessions",
            "auto_save": True,
            "show_progress": True,
            "processing_timeout_ms": 30000,
            "default_question_type": "text",
            "enable_timestamps": True,
            "csv_delimiter": ",",
            "max_sessions_to_keep": 100
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to handle missing keys
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logging.info(f"Settings saved to {self.settings_file}")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value"""
        self.settings[key] = value
        if self.get("auto_save", True):
            self.save_settings()
    
    def update(self, new_settings: Dict[str, Any]):
        """Update multiple settings"""
        self.settings.update(new_settings)
        if self.get("auto_save", True):
            self.save_settings()


class ProgressTracker:
    """Tracks and manages questionnaire progress"""
    
    def __init__(self):
        self.current_question = 0
        self.total_questions = 0
        self.start_time = None
        self.callbacks = []
    
    def set_total_questions(self, total: int):
        """Set the total number of questions"""
        self.total_questions = total
        self.current_question = 0
        self.start_time = datetime.now()
        self._notify_callbacks()
    
    def advance_question(self):
        """Advance to the next question"""
        if self.current_question < self.total_questions:
            self.current_question += 1
            self._notify_callbacks()
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0-100)"""
        if self.total_questions == 0:
            return 0.0
        return (self.current_question / self.total_questions) * 100
    
    def get_estimated_time_remaining(self) -> Optional[float]:
        """Get estimated time remaining in seconds"""
        if not self.start_time or self.current_question == 0:
            return None
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        avg_time_per_question = elapsed_time / self.current_question
        remaining_questions = self.total_questions - self.current_question
        
        return avg_time_per_question * remaining_questions
    
    def add_progress_callback(self, callback):
        """Add a callback function to be called on progress updates"""
        self.callbacks.append(callback)
    
    def remove_progress_callback(self, callback):
        """Remove a progress callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self):
        """Notify all registered callbacks of progress update"""
        for callback in self.callbacks:
            try:
                callback(self.current_question, self.total_questions)
            except Exception as e:
                logging.error(f"Error in progress callback: {e}")
    
    def reset(self):
        """Reset progress tracking"""
        self.current_question = 0
        self.total_questions = 0
        self.start_time = None
        self._notify_callbacks()


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be a safe filename"""
    import re
    return re.sub(r'[\\/*?:"<>|]', "", name)


def cleanup_old_sessions(log_directory: str, max_sessions: int = 100):
    """Clean up old session files to prevent directory bloat"""
    try:
        session_files = []
        for filename in os.listdir(log_directory):
            if filename.startswith('session_') and (filename.endswith('.csv') or filename.endswith('.json')):
                filepath = os.path.join(log_directory, filename)
                mtime = os.path.getmtime(filepath)
                session_files.append((filepath, mtime))
        
        # Sort by modification time (newest first)
        session_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove excess files
        if len(session_files) > max_sessions:
            for filepath, _ in session_files[max_sessions:]:
                try:
                    os.remove(filepath)
                    logging.info(f"Removed old session file: {filepath}")
                except Exception as e:
                    logging.error(f"Error removing old session file {filepath}: {e}")
    
    except Exception as e:
        logging.error(f"Error cleaning up old sessions: {e}")