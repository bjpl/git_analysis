#!/usr/bin/env python3
"""
Simple test to verify test infrastructure is working.
"""

import pytest
import sys
import os


def test_basic_functionality():
    """Test that basic Python functionality works"""
    assert True
    assert 1 + 1 == 2
    assert "hello" == "hello"


def test_imports():
    """Test that required modules can be imported"""
    import json
    import time
    import pathlib
    
    assert json is not None
    assert time is not None
    assert pathlib is not None


def test_ui_imports():
    """Test that UI modules can be imported"""
    try:
        from src.ui.formatter import TerminalFormatter, Color, Theme
        formatter = TerminalFormatter()
        assert formatter is not None
        
        from src.ui.interactive import InteractiveSession
        assert InteractiveSession is not None
        
    except ImportError:
        pytest.skip("UI modules not available")


@pytest.mark.parametrize("value,expected", [
    (1, 1),
    (2, 2),
    ("test", "test"),
])
def test_parametrized(value, expected):
    """Test parametrized functionality"""
    assert value == expected


class TestBasicClass:
    """Test basic class structure"""
    
    def test_method_one(self):
        """Test method one"""
        assert True
    
    def test_method_two(self):
        """Test method two"""
        result = self._helper_method()
        assert result == "helper"
    
    def _helper_method(self):
        """Helper method"""
        return "helper"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])