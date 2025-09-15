#!/usr/bin/env python3
"""Test formatter functionality"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.windows_formatter import WindowsFormatter

def test_formatter():
    """Test the Windows formatter"""
    formatter = WindowsFormatter()
    
    # Test header method - should work without 'style' parameter
    print("\n=== Testing header method ===")
    print(formatter.header("Test Header", level=1))
    print(formatter.header("Test Section", subtitle="With subtitle", level=2))
    
    # Test other methods
    print("\n=== Testing info/success/error methods ===")
    print(formatter.info("This is an info message"))
    print(formatter.success("This is a success message"))
    print(formatter.error("This is an error message"))
    
    # Test code block
    print("\n=== Testing code block ===")
    code = """def hello_world():
    print("Hello, World!")
    return True"""
    print(formatter.code_block(code, title="Example Code"))
    
    print("\n✅ All formatter tests passed!")

if __name__ == "__main__":
    test_formatter()