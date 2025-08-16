# File: main.py
import sys
from PyQt6.QtWidgets import QApplication
from utils.logger import get_logger
from models.database import Database

# Import our MainWindow from the views folder
from views.main_window import MainWindow
from config import WINDOW_WIDTH, WINDOW_HEIGHT

logger = get_logger(__name__)

def main():
    # Initialize the Qt application
    app = QApplication(sys.argv)

    logger.info("Starting My Spanish App...")

    # Optional: Initialize DB for entire application lifecycle
    db = Database()
    db.init_db()

    # Create and show the Main Window
    window = MainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()

    exit_code = app.exec()
    logger.info("Application exited.")
    # Close DB connection before exiting
    db.close()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
