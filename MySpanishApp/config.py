# File: config.py
import os
import logging

# Database settings
DB_FILE = os.path.join(os.path.dirname(__file__), "my_spanish_app.db")

# Logging settings
LOG_LEVEL = logging.DEBUG
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "app.log")
LOG_MAX_BYTES = 1_000_000  # 1 MB
LOG_BACKUP_COUNT = 3

# UI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800