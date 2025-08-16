# File: views/track_tabs/grammar_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, 
    QInputDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from models.grammar_model import GrammarModel
from utils.logger import get_logger

logger = get_logger(__name__)

class GrammarTab(QWidget):
    """
    A tab that shows grammar notes for the selected session
    and allows adding new grammar entries.
    """
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.grammar_model = GrammarModel(self.db)
        self._session_id = None

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel("No session selected.")
        self.layout.addWidget(self.info_label)

        self.grammar_list = QListWidget()
        self.layout.addWidget(self.grammar_list)

        self.add_grammar_btn = QPushButton("Add Grammar")
        self.add_grammar_btn.clicked.connect(self.on_add_grammar)
        self.layout.addWidget(self.add_grammar_btn)

    def set_session_id(self, session_id: int):
        """
        Called by TrackView when the user selects a session.
        """
        self._session_id = session_id
        self.load_grammar()

    def load_grammar(self):
        if not self._session_id:
            self.info_label.setText("No session selected.")
            self.grammar_list.clear()
            return

        self.info_label.setText(f"Grammar for Session ID={self._session_id}")
        self.grammar_list.clear()

        grammar_entries = self.grammar_model.get_grammar_for_session(self._session_id)
        for g in grammar_entries:
            phrase_structure = g["phrase_structure"] or ""
            explanation = g["explanation"] or ""
            display_text = f"{phrase_structure}: {explanation}"
            self.grammar_list.addItem(display_text)

        logger.info(f"Loaded {len(grammar_entries)} grammar items for session {self._session_id}.")

    def on_add_grammar(self):
        if not self._session_id:
            QMessageBox.warning(self, "No Session", "Please select a session first.")
            return
        
        phrase, ok = QInputDialog.getText(self, "New Grammar", "Phrase/Structure:")
        if not ok or not phrase.strip():
            return

        explanation, ok = QInputDialog.getText(self, "New Grammar", "Explanation:")
        if not ok:
            return

        grammar_id = self.grammar_model.add_grammar(
            session_id=self._session_id,
            phrase_structure=phrase.strip(),
            explanation=explanation.strip(),
            resource_link=None
        )

        if grammar_id:
            QMessageBox.information(self, "Success", f"Grammar ID={grammar_id} added.")
            self.load_grammar()
        else:
            QMessageBox.warning(self, "Error", "Failed to add grammar.")
