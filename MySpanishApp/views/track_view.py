# File: views/track_view.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTabWidget, 
    QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from utils.logger import get_logger
from models.database import Database
from models.session_model import SessionModel

# We'll import our specialized tabs for Vocab & Grammar:
from .track_tabs.vocab_tab import VocabTab
from .track_tabs.grammar_tab import GrammarTab
# You can create similar files for Challenges, Comfort, Resources

logger = get_logger(__name__)

class TrackView(QWidget):
    """
    Main widget for the "Track" section.
    Shows a session selector at the top, and 
    a QTabWidget for vocab, grammar, etc. 
    """
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.session_model = SessionModel(self.db)

        self.main_layout = QVBoxLayout(self)

        # 1) Session Selector row
        self.session_selector_layout = QHBoxLayout()
        
        self.session_label = QLabel("Select Session:")
        self.session_combo = QComboBox()
        self.refresh_sessions_btn = QPushButton("Refresh Sessions")

        self.session_selector_layout.addWidget(self.session_label)
        self.session_selector_layout.addWidget(self.session_combo)
        self.session_selector_layout.addWidget(self.refresh_sessions_btn)

        self.main_layout.addLayout(self.session_selector_layout)

        # 2) Tab Widget
        self.tab_widget = QTabWidget()

        # Create tab instances
        self.vocab_tab = VocabTab(db=self.db)
        self.grammar_tab = GrammarTab(db=self.db)

        # (Similarly, you'd add challenges, comfort, resources, notes tabs, etc.)

        self.tab_widget.addTab(self.vocab_tab, "Vocab")
        self.tab_widget.addTab(self.grammar_tab, "Grammar")
        # self.tab_widget.addTab(..., "Challenges")
        # self.tab_widget.addTab(..., "Comfort")
        # self.tab_widget.addTab(..., "Resources")

        self.main_layout.addWidget(self.tab_widget)

        # Signals
        self.refresh_sessions_btn.clicked.connect(self.load_sessions)
        self.session_combo.currentIndexChanged.connect(self.on_session_selected)

        # Initial load
        self.load_sessions()

    def load_sessions(self):
        """
        Fetch sessions from DB and populate the combo box.
        """
        sessions = self.session_model.get_sessions()
        # We'll store them in a list so we can reference by index
        self._sessions_data = sessions

        self.session_combo.clear()
        for s in sessions:
            display_text = f"ID={s['session_id']} | {s['session_date']} {s['start_time']}"
            self.session_combo.addItem(display_text, userData=s["session_id"])

        logger.info(f"Loaded {len(sessions)} sessions into session_combo.")

    def on_session_selected(self, index: int):
        """
        Called when user picks a different session in the combo.
        We'll pass the session_id to each tab so it can display the correct data.
        """
        if index < 0:
            return
        session_id = self.session_combo.itemData(index)
        logger.info(f"Session selected: {session_id}")

        # Update each tab's current session
        self.vocab_tab.set_session_id(session_id)
        self.grammar_tab.set_session_id(session_id)
        # ... for other tabs too
