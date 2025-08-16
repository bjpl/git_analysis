# File: views/settings_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from utils.logger import get_logger
from utils.export import DataExporter
from models.database import Database

logger = get_logger(__name__)

class SettingsView(QWidget):
    """Settings page with export functionality"""
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.exporter = DataExporter(db)
        
        self.layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(title)
        
        # Export section
        export_group = QGroupBox("Data Export")
        export_layout = QVBoxLayout(export_group)
        
        # Export buttons
        self.export_sessions_btn = QPushButton("Export Sessions (CSV)")
        self.export_sessions_btn.clicked.connect(self.export_sessions)
        export_layout.addWidget(self.export_sessions_btn)
        
        self.export_vocab_btn = QPushButton("Export Vocabulary (CSV)")
        self.export_vocab_btn.clicked.connect(self.export_vocab)
        export_layout.addWidget(self.export_vocab_btn)
        
        self.export_all_btn = QPushButton("Export All Data (JSON)")
        self.export_all_btn.clicked.connect(self.export_all)
        export_layout.addWidget(self.export_all_btn)
        
        self.layout.addWidget(export_group)
        
        # Add stretch to push everything to top
        self.layout.addStretch()
    
    def export_sessions(self):
        """Export sessions to CSV"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Sessions", "sessions.csv", "CSV Files (*.csv)"
        )
        if filepath:
            if self.exporter.export_sessions_csv(filepath):
                QMessageBox.information(self, "Success", f"Sessions exported to {filepath}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export sessions")
    
    def export_vocab(self):
        """Export vocabulary to CSV"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Vocabulary", "vocabulary.csv", "CSV Files (*.csv)"
        )
        if filepath:
            if self.exporter.export_vocab_csv(filepath):
                QMessageBox.information(self, "Success", f"Vocabulary exported to {filepath}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export vocabulary")
    
    def export_all(self):
        """Export all data to JSON"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export All Data", "spanish_app_data.json", "JSON Files (*.json)"
        )
        if filepath:
            if self.exporter.export_all_json(filepath):
                QMessageBox.information(self, "Success", f"All data exported to {filepath}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export data")