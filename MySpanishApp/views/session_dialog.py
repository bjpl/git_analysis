# File: views/session_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from utils.logger import get_logger

logger = get_logger(__name__)

class SessionDialog(QDialog):
    """
    A small dialog to gather session info:
    - teacher_id (or teacher name)
    - date
    - start time
    - duration
    """
    def __init__(self, default_date: QDate, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Session")
        self.resize(300, 200)

        # Layout
        self.main_layout = QVBoxLayout(self)

        # Teacher ID / Name (for now, let's do a simple line edit)
        self.teacher_label = QLabel("Teacher ID:")
        self.teacher_edit = QLineEdit()
        self.teacher_edit.setText("1")  # or blank
        self.main_layout.addWidget(self.teacher_label)
        self.main_layout.addWidget(self.teacher_edit)

        # Date
        self.date_label = QLabel("Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(default_date)  # pre-fill from clicked date
        self.main_layout.addWidget(self.date_label)
        self.main_layout.addWidget(self.date_edit)

        # Start Time
        self.time_label = QLabel("Start Time (HH:MM):")
        self.time_edit = QLineEdit("17:00")
        self.main_layout.addWidget(self.time_label)
        self.main_layout.addWidget(self.time_edit)

        # Duration
        self.duration_label = QLabel("Duration:")
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["1h", "30m"])
        self.main_layout.addWidget(self.duration_label)
        self.main_layout.addWidget(self.duration_combo)

        # Buttons (Save/Cancel)
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.main_layout.addLayout(btn_layout)

    def validate_and_accept(self):
        """Validate form data before accepting"""
        teacher_id = self.teacher_edit.text().strip()
        start_time = self.time_edit.text().strip()
        
        if not teacher_id:
            QMessageBox.warning(self, "Validation Error", "Teacher ID is required")
            return
            
        if not start_time:
            QMessageBox.warning(self, "Validation Error", "Start time is required")
            return
            
        try:
            int(teacher_id)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Teacher ID must be a number")
            return
            
        self.accept()

    def get_form_data(self):
        """
        Retrieve the form data as a dict.
        """
        return {
            "teacher_id": int(self.teacher_edit.text()),
            "session_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "start_time": self.time_edit.text(),
            "duration": self.duration_combo.currentText()
        }
