"""
Structured logging configuration for Learning Voice Agent
PATTERN: Centralized logging with consistent formatting
"""
import logging
import sys
from typing import Optional

def setup_logger(
    name: str = "voice_agent",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up structured logging with consistent formatting
    
    Args:
        name: Logger name (defaults to 'voice_agent')
        level: Logging level (defaults to INFO)
        format_string: Custom format string (optional)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    
    # Default format with useful information
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

# Global logger instance
logger = setup_logger()

# Specialized loggers for different components
api_logger = setup_logger("voice_agent.api")
audio_logger = setup_logger("voice_agent.audio")
db_logger = setup_logger("voice_agent.database")
conversation_logger = setup_logger("voice_agent.conversation")