import logging
import os
from datetime import datetime
from pathlib import Path

class ImageManagerLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        log_file = self.log_dir / f"image_manager_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging
        self.logger = logging.getLogger("ImageManager")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for all logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for warnings and errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("="*50)
        self.logger.info("Image Manager Started")
        self.logger.info("="*50)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        self.logger.critical(message, exc_info=exc_info)
    
    def log_operation(self, operation, details=None, success=True):
        """Log a specific operation with details"""
        status = "SUCCESS" if success else "FAILED"
        msg = f"Operation: {operation} - {status}"
        if details:
            msg += f" - Details: {details}"
        
        if success:
            self.logger.info(msg)
        else:
            self.logger.error(msg)
    
    def get_log_files(self):
        """Return list of log files"""
        return sorted(self.log_dir.glob("*.log"))
    
    def cleanup_old_logs(self, days=30):
        """Remove log files older than specified days"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in self.get_log_files():
            # Get file modification time
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                try:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to delete log file {log_file.name}: {e}")

# Global logger instance
logger = ImageManagerLogger()