# File: views/track_tabs/vocab_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, 
    QInputDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from models.vocab_model import VocabModel
from utils.logger import get_logger

logger = get_logger(__name__)

class VocabTab(QWidget):
    """
    A tab that shows vocab items for the selected session
    and allows adding new vocab entries.
    """
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.vocab_model = VocabModel(self.db)
        self._session_id = None

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel("No session selected.")
        self.layout.addWidget(self.info_label)

        self.vocab_list = QListWidget()
        self.layout.addWidget(self.vocab_list)

        # Buttons layout - horizontal for better space usage
        buttons_layout = QHBoxLayout()
        self.add_vocab_btn = QPushButton("Add Vocab")
        self.add_vocab_btn.clicked.connect(self.on_add_vocab)
        
        self.delete_vocab_btn = QPushButton("Delete Selected")
        self.delete_vocab_btn.clicked.connect(self.on_delete_vocab)
        self.delete_vocab_btn.setEnabled(False)  # Disabled until selection
        
        buttons_layout.addWidget(self.add_vocab_btn)
        buttons_layout.addWidget(self.delete_vocab_btn)
        buttons_layout.addStretch()  # Push buttons to left
        self.layout.addLayout(buttons_layout)
        
        # Connect selection changed signal
        self.vocab_list.itemSelectionChanged.connect(self.on_selection_changed)

    def set_session_id(self, session_id: int):
        """
        Called by TrackView when the user selects a session.
        """
        self._session_id = session_id
        self.load_vocab()

    def load_vocab(self):
        if not self._session_id:
            self.info_label.setText("No session selected.")
            self.vocab_list.clear()
            return

        self.info_label.setText(f"Vocab for Session ID={self._session_id}")
        self.vocab_list.clear()

        vocab_entries = self.vocab_model.get_vocab_for_session(self._session_id)
        for v in vocab_entries:
            word_phrase = v["word_phrase"]
            translation = v["translation"] or ""
            countries = v["countries"] or ""  # from GROUP_CONCAT
            display_text = f"{word_phrase} -> {translation} (Regions: {countries})"
            self.vocab_list.addItem(display_text)
            # Store vocab_id for deletion
            item = self.vocab_list.item(self.vocab_list.count()-1)
            item.setData(Qt.ItemDataRole.UserRole, v['vocab_id'])

        logger.info(f"Loaded {len(vocab_entries)} vocab items for session {self._session_id}.")

    def on_add_vocab(self):
        """
        Prompt user to enter new vocab item.
        """
        if not self._session_id:
            QMessageBox.warning(self, "No Session", "Please select a session first.")
            return
        
        # We'll do a simple QInputDialog chain for word, translation, regions.
        word, ok = QInputDialog.getText(self, "New Vocab", "Word/Phrase:")
        if not ok or not word.strip():
            return
        
        translation, ok = QInputDialog.getText(self, "New Vocab", "Translation:")
        if not ok:
            return
        
        regions, ok = QInputDialog.getText(self, "New Vocab", "Regions (comma-separated):")
        if not ok:
            return

        regions_list = [r.strip() for r in regions.split(",") if r.strip()]

        vocab_id = self.vocab_model.add_vocab(
            session_id=self._session_id,
            word_phrase=word.strip(),
            translation=translation.strip(),
            context_notes="(added via TrackView)",
            regionalisms=regions_list
        )

        if vocab_id:
            QMessageBox.information(self, "Success", f"Vocab ID={vocab_id} added.")
            self.load_vocab()
        else:
            QMessageBox.warning(self, "Error", "Failed to add vocab.")
    
    def on_selection_changed(self):
        """Enable/disable delete button based on selection"""
        self.delete_vocab_btn.setEnabled(bool(self.vocab_list.currentItem()))
    
    def on_delete_vocab(self):
        """Delete the selected vocabulary item"""
        current_item = self.vocab_list.currentItem()
        if not current_item:
            return
            
        vocab_id = current_item.data(Qt.ItemDataRole.UserRole)
        if not vocab_id:
            QMessageBox.warning(self, "Error", "Could not get vocab ID")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Delete vocabulary item: {current_item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.vocab_model.delete_vocab(vocab_id):
                QMessageBox.information(self, "Success", "Vocabulary item deleted.")
                self.load_vocab()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete vocabulary item.")
