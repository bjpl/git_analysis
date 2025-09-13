#!/usr/bin/env python3
"""
UI Components Package - Enhanced terminal interface components

This package provides beautiful visual components for CLI applications:
- Gradient text effects
- Loading animations and spinners  
- Formatted data tables
- Progress visualizations and charts
- Interactive prompts with validation
"""

try:
    from .gradient import (
        GradientText, GradientPreset, GradientDirection,
        gradient, rainbow, fire, ocean, cyberpunk, galaxy
    )
    GRADIENT_AVAILABLE = True
except ImportError:
    GRADIENT_AVAILABLE = False

try:
    from .animations import (
        LoadingAnimation, SpinnerStyle, AnimationSpeed,
        SpinnerContext, AnimatedProgressBar, ProgressStyle,
        spinner_task, create_spinner
    )
    ANIMATIONS_AVAILABLE = True
except ImportError:
    ANIMATIONS_AVAILABLE = False

try:
    from .tables import (
        DataTable, TableStyle, ColumnAlignment, ColumnConfig,
        create_table, currency_formatter, percentage_formatter,
        number_formatter, status_color_func
    )
    TABLES_AVAILABLE = True
except ImportError:
    TABLES_AVAILABLE = False

try:
    from .charts import (
        ProgressBar, BarChart, LineChart, PieChart, Sparkline,
        ChartStyle, ProgressStyle, DataPoint,
        progress_bar, bar_chart, line_chart, pie_chart, sparkline
    )
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

try:
    from .prompts import (
        InputPrompt, MenuSelector, PromptStyle, ValidationResult, ValidationResponse,
        ask_text, ask_number, ask_choice, ask_confirm, ask_password, show_menu,
        email_validator, url_validator, phone_validator, length_validator
    )
    PROMPTS_AVAILABLE = True
except ImportError:
    PROMPTS_AVAILABLE = False

# Component availability flags
COMPONENTS_AVAILABLE = all([
    GRADIENT_AVAILABLE,
    ANIMATIONS_AVAILABLE, 
    TABLES_AVAILABLE,
    CHARTS_AVAILABLE,
    PROMPTS_AVAILABLE
])

__all__ = [
    # Availability flags
    'COMPONENTS_AVAILABLE', 'GRADIENT_AVAILABLE', 'ANIMATIONS_AVAILABLE',
    'TABLES_AVAILABLE', 'CHARTS_AVAILABLE', 'PROMPTS_AVAILABLE',
    
    # Gradient components
    'GradientText', 'GradientPreset', 'GradientDirection',
    'gradient', 'rainbow', 'fire', 'ocean', 'cyberpunk', 'galaxy',
    
    # Animation components
    'LoadingAnimation', 'SpinnerStyle', 'AnimationSpeed',
    'SpinnerContext', 'AnimatedProgressBar', 'ProgressStyle',
    'spinner_task', 'create_spinner',
    
    # Table components
    'DataTable', 'TableStyle', 'ColumnAlignment', 'ColumnConfig',
    'create_table', 'currency_formatter', 'percentage_formatter',
    'number_formatter', 'status_color_func',
    
    # Chart components
    'ProgressBar', 'BarChart', 'LineChart', 'PieChart', 'Sparkline',
    'ChartStyle', 'DataPoint', 'progress_bar', 'bar_chart', 
    'line_chart', 'pie_chart', 'sparkline',
    
    # Prompt components
    'InputPrompt', 'MenuSelector', 'PromptStyle', 'ValidationResult', 
    'ValidationResponse', 'ask_text', 'ask_number', 'ask_choice', 
    'ask_confirm', 'ask_password', 'show_menu', 'email_validator', 
    'url_validator', 'phone_validator', 'length_validator'
]


def get_component_status():
    """Get status of all components
    
    Returns:
        Dict with component availability status
    """
    return {
        'gradient': GRADIENT_AVAILABLE,
        'animations': ANIMATIONS_AVAILABLE,
        'tables': TABLES_AVAILABLE,
        'charts': CHARTS_AVAILABLE,
        'prompts': PROMPTS_AVAILABLE,
        'all_available': COMPONENTS_AVAILABLE
    }


def create_enhanced_formatter():
    """Create an enhanced formatter with all available components
    
    Returns:
        Enhanced formatter instance or None if components unavailable
    """
    if not COMPONENTS_AVAILABLE:
        return None
    
    # This would be implemented to create a unified formatter
    # that uses all available components
    pass