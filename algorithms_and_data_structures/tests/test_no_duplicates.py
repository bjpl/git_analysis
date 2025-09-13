#!/usr/bin/env python3
"""
Test script to verify no duplicate output in CLI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.formatter import TerminalFormatter

def test_formatter_no_duplicates():
    """Test that formatter methods don't produce duplicate output"""
    print("Testing formatter methods for duplicate output...")
    
    formatter = TerminalFormatter()
    
    # These should each print exactly once
    print("\n--- Testing success message ---")
    formatter.success("This should appear only once")
    
    print("\n--- Testing error message ---")
    formatter.error("This error should appear only once")
    
    print("\n--- Testing warning message ---")
    formatter.warning("This warning should appear only once")
    
    print("\n--- Testing info message ---")
    formatter.info("This info should appear only once")
    
    print("\n--- Testing header ---")
    formatter.header("This header should appear only once")
    
    print("\n✅ Test complete! Check above for any duplicate messages.")

if __name__ == "__main__":
    test_formatter_no_duplicates()