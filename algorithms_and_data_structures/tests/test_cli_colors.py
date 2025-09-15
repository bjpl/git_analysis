#!/usr/bin/env python3
"""Test script to verify CLI colors and formatting are working"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Force colorama initialization
import colorama
colorama.init(autoreset=False, convert=True, strip=False)

# Now import our formatter
from src.ui.windows_formatter import WindowsFormatter, WindowsColor

def test_colors():
    """Test all color outputs"""
    formatter = WindowsFormatter()
    
    print("Testing Windows Formatter Colors:")
    print("=" * 50)
    
    # Test basic color methods
    print(formatter.success("✓ Success message (should be green)"))
    print(formatter.error("✗ Error message (should be red)"))
    print(formatter.warning("⚠ Warning message (should be yellow)"))
    print(formatter.info("ℹ Info message (should be cyan/blue)"))
    
    print("\nDirect color tests:")
    print(f"{WindowsColor.GREEN.value}Green text{WindowsColor.RESET.value}")
    print(f"{WindowsColor.BRIGHT_CYAN.value}Bright cyan text{WindowsColor.RESET.value}")
    print(f"{WindowsColor.BRIGHT_YELLOW.value}Bright yellow text{WindowsColor.RESET.value}")
    print(f"{WindowsColor.BRIGHT_MAGENTA.value}Bright magenta text{WindowsColor.RESET.value}")
    
    print("\nBox test:")
    print(formatter.box("This is a test box\nWith multiple lines", title="TEST BOX"))
    
    print("\nHeader test:")
    print(formatter.header("MAIN HEADER", "Subtitle here"))
    
    print("\nDivider test:")
    print(formatter.divider("Section Title"))
    
    print("\nProgress bar test:")
    progress_bar = formatter.progress_bar(65, 100, "Progress")
    print(progress_bar)
    
    print("\nColors enabled:", formatter.colors_enabled)
    print("Box style:", formatter.box_style)

if __name__ == "__main__":
    test_colors()
    print("\n✅ Test completed! If you see colors above, everything is working!")