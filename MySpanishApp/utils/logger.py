import logging
from logging.handlers import RotatingFileHandler
import os
from config import LOG_LEVEL, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT

# Create logs directory if it doesn't exist
LOG_DIR = os.path.dirname(LOG_FILE)
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)

        # Rotating file handler
        fh = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        fh.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    return logger
