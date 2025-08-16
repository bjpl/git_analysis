# File: views/review_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QListWidget, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from utils.logger import get_logger
from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel

logger = get_logger(__name__)

class ReviewView(QWidget):
    """Simple review and summary view for learning progress"""
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.session_model = SessionModel(db)
        self.vocab_model = VocabModel(db)
        
        self.layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Learning Review & Summary")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(title)
        
        # Stats section
        self.create_stats_section()
        
        # Recent sessions section
        self.create_recent_sessions_section()
        
        # Vocabulary overview section
        self.create_vocab_section()
        
        # Refresh data on load
        self.refresh_data()
    
    def create_stats_section(self):
        """Create statistics overview section"""
        stats_group = QGroupBox("Learning Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.total_sessions_label = QLabel("Total Sessions: -")
        self.completed_sessions_label = QLabel("Completed Sessions: -")
        self.total_vocab_label = QLabel("Total Vocabulary: -")
        self.recent_activity_label = QLabel("Recent Activity: -")
        
        stats_layout.addWidget(self.total_sessions_label)
        stats_layout.addWidget(self.completed_sessions_label)
        stats_layout.addWidget(self.total_vocab_label)
        stats_layout.addWidget(self.recent_activity_label)
        
        self.layout.addWidget(stats_group)
    
    def create_recent_sessions_section(self):
        """Create recent sessions section"""
        sessions_group = QGroupBox("Recent Sessions")
        sessions_layout = QVBoxLayout(sessions_group)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Show:"))
        
        self.session_filter = QComboBox()
        self.session_filter.addItems(["All Sessions", "Completed Only", "Planned Only"])
        self.session_filter.currentTextChanged.connect(self.refresh_sessions)
        filter_layout.addWidget(self.session_filter)
        filter_layout.addStretch()
        
        sessions_layout.addLayout(filter_layout)
        
        self.recent_sessions_list = QListWidget()
        self.recent_sessions_list.setMaximumHeight(150)
        sessions_layout.addWidget(self.recent_sessions_list)
        
        self.layout.addWidget(sessions_group)
    
    def create_vocab_section(self):
        """Create vocabulary overview section"""
        vocab_group = QGroupBox("Recent Vocabulary")
        vocab_layout = QVBoxLayout(vocab_group)
        
        self.recent_vocab_list = QListWidget()
        self.recent_vocab_list.setMaximumHeight(150)
        vocab_layout.addWidget(self.recent_vocab_list)
        
        self.layout.addWidget(vocab_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        self.layout.addWidget(refresh_btn)
        
        # Add stretch to push everything to top
        self.layout.addStretch()
    
    def refresh_data(self):
        """Refresh all data displays"""
        self.refresh_stats()
        self.refresh_sessions()
        self.refresh_vocab()
    
    def refresh_stats(self):
        """Update statistics labels"""
        try:
            # Get all sessions
            all_sessions = self.session_model.get_sessions()
            total_sessions = len(all_sessions)
            completed_sessions = len([s for s in all_sessions if s.get('status') == 'completed'])
            
            # Get total vocabulary count
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM vocab")
            total_vocab = cursor.fetchone()['count']
            
            # Recent activity (sessions in last 7 days)
            from datetime import datetime, timedelta
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            recent_sessions = [s for s in all_sessions if s.get('session_date', '') >= week_ago]
            
            self.total_sessions_label.setText(f"Total Sessions: {total_sessions}")
            self.completed_sessions_label.setText(f"Completed Sessions: {completed_sessions}")
            self.total_vocab_label.setText(f"Total Vocabulary: {total_vocab}")
            self.recent_activity_label.setText(f"Sessions This Week: {len(recent_sessions)}")
            
        except Exception as e:
            logger.error(f"Error refreshing stats: {e}")
    
    def refresh_sessions(self):
        """Update recent sessions list"""
        try:
            self.recent_sessions_list.clear()
            all_sessions = self.session_model.get_sessions()
            
            # Apply filter
            filter_text = self.session_filter.currentText()
            if filter_text == "Completed Only":
                sessions = [s for s in all_sessions if s.get('status') == 'completed']
            elif filter_text == "Planned Only":
                sessions = [s for s in all_sessions if s.get('status') == 'planned']
            else:
                sessions = all_sessions
            
            # Show most recent 10
            recent_sessions = sorted(sessions, key=lambda x: x.get('session_date', ''), reverse=True)[:10]
            
            for session in recent_sessions:
                display_text = f"{session['session_date']} | {session['start_time']} | {session.get('status', 'unknown').title()}"
                self.recent_sessions_list.addItem(display_text)
                
        except Exception as e:
            logger.error(f"Error refreshing sessions: {e}")
    
    def refresh_vocab(self):
        """Update recent vocabulary list"""
        try:
            self.recent_vocab_list.clear()
            
            # Get recent vocabulary across all sessions
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT v.word_phrase, v.translation, s.session_date
                FROM vocab v
                JOIN sessions s ON v.session_id = s.session_id
                ORDER BY v.vocab_id DESC
                LIMIT 15
            """)
            recent_vocab = cursor.fetchall()
            
            for vocab in recent_vocab:
                display_text = f"{vocab['word_phrase']} → {vocab['translation']} ({vocab['session_date']})"
                self.recent_vocab_list.addItem(display_text)
                
        except Exception as e:
            logger.error(f"Error refreshing vocabulary: {e}")