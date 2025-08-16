# File: views/plan_view.py
from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QCalendarWidget, 
    QPushButton, 
    QListWidget, 
    QLabel, 
    QMessageBox,
    QLineEdit,
    QMenu
)
from PyQt6.QtCore import QDate, Qt
from utils.logger import get_logger
from models.session_model import SessionModel
from models.database import Database
from .session_dialog import SessionDialog

logger = get_logger(__name__)

class PlanView(QWidget):
    """
    The main widget for the "Plan" section.
    Displays a QCalendarWidget on the left and 
    a list of sessions for the selected date on the right,
    plus an "Add Session" button.
    """
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.session_model = SessionModel(self.db)

        # Layouts
        self.main_layout = QHBoxLayout(self)
        
        # 1) Calendar on the left
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_calendar_date_clicked)

        # 2) Right side: vertical layout with session list + "Add Session" button
        self.right_layout = QVBoxLayout()
        self.session_list = QListWidget()
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_context_menu)
        
        self.add_session_btn = QPushButton("Add Session")
        self.add_session_btn.clicked.connect(self.on_add_session_clicked)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search sessions...")
        self.search_box.textChanged.connect(self.filter_sessions)
        
        self.right_layout.addWidget(QLabel("Sessions for selected date:"))
        self.right_layout.addWidget(self.search_box)
        self.right_layout.addWidget(self.session_list)
        self.right_layout.addWidget(self.add_session_btn)

        # Put them together
        self.main_layout.addWidget(self.calendar, 1)
        self.main_layout.addLayout(self.right_layout, 2)

        # Initial load
        self.selected_date = self.calendar.selectedDate()
        self.all_sessions = []  # Store all sessions for filtering
        self.load_sessions_for_date(self.selected_date)

    def on_calendar_date_clicked(self, qdate: QDate):
        """
        Triggered when the user clicks a date in the calendar.
        """
        self.selected_date = qdate
        self.load_sessions_for_date(qdate)

    def load_sessions_for_date(self, qdate: QDate):
        """
        Fetch sessions from DB for the given date and populate the list.
        """
        self.selected_date = qdate
        date_str = qdate.toString("yyyy-MM-dd")
        all_sessions = self.session_model.get_sessions()

        # Filter sessions for this date and store them
        self.all_sessions = [s for s in all_sessions if s["session_date"] == date_str]
        
        self.filter_sessions()  # Apply current search filter
        logger.info(f"Loaded {len(self.all_sessions)} sessions for {date_str}.")
    
    def filter_sessions(self):
        """Filter sessions based on search text"""
        search_text = self.search_box.text().lower()
        
        self.session_list.clear()
        for s in self.all_sessions:
            # Search in session details
            searchable_text = f"{s['session_id']} {s['start_time']} {s['duration']} {s.get('status', '')}"
            if search_text in searchable_text.lower():
                display_text = f"ID={s['session_id']} | Time={s['start_time']} | Duration={s['duration']} | Status={s['status']}"
                self.session_list.addItem(display_text)
                # Store session data for context menu
                item = self.session_list.item(self.session_list.count()-1)
                item.setData(Qt.ItemDataRole.UserRole, s['session_id'])

    def on_add_session_clicked(self):
        """
        Opens a dialog to add a new session for the selected date.
        """
        dialog = SessionDialog(self.selected_date, self)
        if dialog.exec():
            # If user clicked "Save"
            data = dialog.get_form_data()
            # Insert into DB
            session_id = self.session_model.create_session(
                teacher_id=data["teacher_id"],  # or store teacher name in DB if not using teacher table
                session_date=data["session_date"],
                start_time=data["start_time"],
                duration=data["duration"],
                status="planned"
            )
            if session_id:
                QMessageBox.information(self, "Session Added", f"Session created with ID={session_id}")
                # Refresh the session list
                self.load_sessions_for_date(self.selected_date)
            else:
                QMessageBox.warning(self, "Error", "Failed to create session in DB.")
    
    def show_context_menu(self, position):
        """Show context menu for session items"""
        item = self.session_list.itemAt(position)
        if not item:
            return
            
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if not session_id:
            return
            
        menu = QMenu(self)
        
        # Status change actions
        planned_action = menu.addAction("Mark as Planned")
        planned_action.triggered.connect(lambda: self.change_session_status(session_id, "planned"))
        
        completed_action = menu.addAction("Mark as Completed")
        completed_action.triggered.connect(lambda: self.change_session_status(session_id, "completed"))
        
        cancelled_action = menu.addAction("Mark as Cancelled")
        cancelled_action.triggered.connect(lambda: self.change_session_status(session_id, "cancelled"))
        
        menu.exec(self.session_list.mapToGlobal(position))
    
    def change_session_status(self, session_id, new_status):
        """Change the status of a session"""
        rows_affected = self.session_model.update_session_status(session_id, new_status)
        if rows_affected > 0:
            QMessageBox.information(self, "Success", f"Session status updated to '{new_status}'")
            self.load_sessions_for_date(self.selected_date)  # Refresh the list
        else:
            QMessageBox.warning(self, "Error", "Failed to update session status")
