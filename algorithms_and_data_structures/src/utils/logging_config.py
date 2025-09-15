"""
Logging Configuration - Centralized logging setup for the application
Provides structured logging with multiple handlers and formatters.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from rich.logging import RichHandler
from rich.console import Console


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for different log levels."""
    
    COLORS = {
        logging.DEBUG: '\033[36m',    # Cyan
        logging.INFO: '\033[32m',     # Green
        logging.WARNING: '\033[33m',  # Yellow
        logging.ERROR: '\033[31m',    # Red
        logging.CRITICAL: '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelno in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelno]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(level: str = 'INFO', 
                 log_file: Optional[str] = None,
                 enable_rich: bool = True,
                 config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional log file path
        enable_rich: Enable rich console logging
        config: Optional additional configuration
        
    Returns:
        Configured root logger
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create logs directory
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"adaptive_learning_{timestamp}.log"
    
    # Console handler with Rich formatting
    if enable_rich:
        console = Console()
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            enable_link_path=False,
            markup=True
        )
        console_handler.setLevel(numeric_level)
        
        # Rich formatter
        rich_formatter = logging.Formatter(
            fmt="%(message)s",
            datefmt="[%X]"
        )
        console_handler.setFormatter(rich_formatter)
    else:
        # Standard console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        # Colored formatter for standard console
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handler with detailed formatting
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Always log debug to file
    
    # Detailed file formatter
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors)
    error_log_path = Path(log_file).parent / f"error_{Path(log_file).name}"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Configure third-party loggers
    _configure_third_party_loggers(numeric_level)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Error log: {error_log_path}")
    
    return root_logger


def _configure_third_party_loggers(level: int):
    """Configure logging levels for third-party libraries."""
    third_party_loggers = {
        'sqlalchemy.engine': logging.WARNING,
        'sqlalchemy.pool': logging.WARNING, 
        'alembic': logging.INFO,
        'matplotlib': logging.WARNING,
        'PIL': logging.WARNING,
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'httpx': logging.WARNING
    }
    
    for logger_name, log_level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(max(level, log_level))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggingContext:
    """Context manager for temporarily changing logging configuration."""
    
    def __init__(self, level: str, logger_name: Optional[str] = None):
        """
        Initialize logging context.
        
        Args:
            level: Temporary logging level
            logger_name: Optional specific logger name
        """
        self.level = level
        self.logger_name = logger_name
        self.original_level = None
        self.logger = None
    
    def __enter__(self):
        """Enter context and change logging level."""
        self.logger = logging.getLogger(self.logger_name)
        self.original_level = self.logger.level
        self.logger.setLevel(getattr(logging, self.level.upper()))
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original logging level."""
        if self.logger and self.original_level is not None:
            self.logger.setLevel(self.original_level)


class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self, name: str = "performance"):
        """Initialize performance logger."""
        self.logger = get_logger(name)
        self.start_times: Dict[str, datetime] = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = datetime.now()
        self.logger.debug(f"Started timing: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and log the duration."""
        if operation not in self.start_times:
            self.logger.warning(f"No start time found for operation: {operation}")
            return 0.0
        
        duration = (datetime.now() - self.start_times[operation]).total_seconds()
        self.logger.info(f"Operation '{operation}' took {duration:.3f} seconds")
        del self.start_times[operation]
        return duration
    
    def log_metric(self, metric_name: str, value: Any, unit: str = ""):
        """Log a performance metric."""
        unit_str = f" {unit}" if unit else ""
        self.logger.info(f"Metric '{metric_name}': {value}{unit_str}")


class SecurityLogger:
    """Specialized logger for security events."""
    
    def __init__(self):
        """Initialize security logger."""
        self.logger = get_logger("security")
        
        # Setup separate security log file
        security_log_path = Path("logs") / "security.log"
        security_log_path.parent.mkdir(exist_ok=True)
        
        # Security file handler
        security_handler = logging.handlers.RotatingFileHandler(
            security_log_path,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.INFO)
        
        # Security formatter with extra fields
        security_formatter = logging.Formatter(
            fmt='%(asctime)s - SECURITY - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        security_handler.setFormatter(security_formatter)
        
        self.logger.addHandler(security_handler)
    
    def log_authentication_attempt(self, username: str, success: bool, ip_address: str = "unknown"):
        """Log authentication attempt."""
        status = "SUCCESS" if success else "FAILURE" 
        self.logger.info(f"Authentication {status} - User: {username}, IP: {ip_address}")
    
    def log_suspicious_activity(self, activity: str, details: str = ""):
        """Log suspicious activity."""
        self.logger.warning(f"Suspicious activity: {activity} - {details}")
    
    def log_data_access(self, user: str, resource: str, action: str):
        """Log data access events."""
        self.logger.info(f"Data access - User: {user}, Resource: {resource}, Action: {action}")


# Global performance logger instance
perf_logger = PerformanceLogger()

# Global security logger instance  
security_logger = SecurityLogger()