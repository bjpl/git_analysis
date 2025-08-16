# File: views/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from utils.logger import get_logger
from models.database import Database
from .plan_view import PlanView
from .track_view import TrackView
from .review_view import ReviewView
from .settings_view import SettingsView

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window with a sidebar to switch between
    Plan, Track, Review, and Settings sections.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Spanish Tutor Planner")

        # --- Initialize Database ---
        self.db = Database()
        self.db.init_db()

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        # --- Sidebar (Navigation) ---
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(10)

        # Nav Buttons with icons/styling
        self.plan_button = QPushButton("📅 Plan")
        self.track_button = QPushButton("📝 Track") 
        self.review_button = QPushButton("📊 Review")
        self.settings_button = QPushButton("⚙️ Settings")

        # Add buttons to sidebar with consistent styling
        buttons = [self.plan_button, self.track_button, self.review_button, self.settings_button]
        for btn in buttons:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("QPushButton { text-align: left; padding: 8px; }")
            self.sidebar_layout.addWidget(btn)
        
        self.sidebar_layout.addStretch()  # push buttons to top

        # Sidebar size constraints
        self.sidebar_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # --- Stacked Widget (Main Content) ---
        self.stacked_widget = QStackedWidget()

        # Pages: Plan, Track, Review, Settings
        self.plan_page = PlanView(self.db)
        self.track_page = TrackView(self.db)
        self.review_page = ReviewView(self.db)
        self.settings_page = SettingsView(self.db)

        self.stacked_widget.addWidget(self.plan_page)    # index 0
        self.stacked_widget.addWidget(self.track_page)   # index 1
        self.stacked_widget.addWidget(self.review_page)  # index 2
        self.stacked_widget.addWidget(self.settings_page)# index 3

        # Show Plan page by default
        self.stacked_widget.setCurrentIndex(0)

        # --- Assemble Main Layout ---
        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.stacked_widget)

        # --- Connect Signals ---
        self.plan_button.clicked.connect(self.show_plan_page)
        self.track_button.clicked.connect(self.show_track_page)
        self.review_button.clicked.connect(self.show_review_page)
        self.settings_button.clicked.connect(self.show_settings_page)
        
        # --- Keyboard Shortcuts ---
        self.setup_shortcuts()

        logger.info("MainWindow initialized with PlanView.")

    def create_placeholder_page(self, text: str) -> QWidget:
        """
        Creates a simple placeholder page with a label.
        Replace this with a real widget (TrackView, ReviewView, etc.) 
        once you build those sections.
        """
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page_widget

    def show_plan_page(self):
        logger.info("Switching to Plan page.")
        self.stacked_widget.setCurrentIndex(0)

    def show_track_page(self):
        logger.info("Switching to Track page.")
        self.stacked_widget.setCurrentIndex(1)

    def show_review_page(self):
        logger.info("Switching to Review page.")
        self.stacked_widget.setCurrentIndex(2)

    def show_settings_page(self):
        logger.info("Switching to Settings page.")
        self.stacked_widget.setCurrentIndex(3)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        # Navigation shortcuts
        QShortcut(QKeySequence("Ctrl+1"), self, self.show_plan_page)
        QShortcut(QKeySequence("Ctrl+2"), self, self.show_track_page)
        QShortcut(QKeySequence("Ctrl+3"), self, self.show_review_page)
        QShortcut(QKeySequence("Ctrl+4"), self, self.show_settings_page)
        
        # App shortcuts
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F1"), self, self.show_help)
    
    def show_help(self):
        """Show keyboard shortcuts help"""
        from PyQt6.QtWidgets import QMessageBox
        help_text = """
Keyboard Shortcuts:
• Ctrl+1 - Plan view
• Ctrl+2 - Track view  
• Ctrl+3 - Review view
• Ctrl+4 - Settings view
• Ctrl+Q - Quit application
• F1 - Show this help
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text.strip())

    def closeEvent(self, event):
        """
        Called when the main window is closing. 
        We'll close the DB connection here.
        """
        logger.info("MainWindow close event triggered. Closing DB.")
        self.db.close()
        super().closeEvent(event)
