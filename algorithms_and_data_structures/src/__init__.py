#!/usr/bin/env python3
"""
Curriculum CLI - Beautiful and robust CLI for curriculum and content management

This package provides a modular, extensible CLI architecture with:
- Command pattern implementation
- Plugin system
- Beautiful terminal formatting
- Interactive and non-interactive modes
- Configuration management
- Error handling and validation
"""

__version__ = "1.0.0"
__author__ = "CLI Architecture Team"
__description__ = "Beautiful and robust CLI for curriculum and content management"

from .cli import AlgorithmLearningCLI
from .config import Config

__all__ = [
    'AlgorithmLearningCLI',
    'Config'
]
