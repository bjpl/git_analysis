#!/usr/bin/env python3
"""
Test script for the Enhanced Interactive Learning System
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_interactive():
    """Test the enhanced interactive system"""
    try:
        from src.ui.enhanced_interactive import EnhancedInteractiveSession
        
        print("🧪 Testing Enhanced Interactive Learning System...")
        print("This will launch the full enhanced interface with all features.\n")
        
        # Create and run enhanced session
        session = EnhancedInteractiveSession()
        asyncio.run(session.run())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some dependencies may be missing.")
        return False
    except KeyboardInterrupt:
        print("\n👋 Test interrupted. That's expected!")
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    return True

def test_components():
    """Test individual components"""
    print("🧪 Testing Individual Components...")
    
    # Test formatter
    try:
        from src.ui.formatter import TerminalFormatter, Color
        formatter = TerminalFormatter()
        print("✅ TerminalFormatter: OK")
        
        # Test typing animation
        async def test_typing():
            await formatter.type_text("Testing typing animation...", speed=0.01)
        
        asyncio.run(test_typing())
        print("✅ Typing Animation: OK")
        
    except Exception as e:
        print(f"❌ Formatter test failed: {e}")
        return False
    
    # Test navigation
    try:
        from src.ui.navigation import NavigationController, MenuItem
        nav = NavigationController(formatter)
        print("✅ NavigationController: OK")
        
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
        return False
    
    # Test notes system
    try:
        from src.ui.notes import NotesManager, RichNote, NoteType, Priority
        notes_manager = NotesManager(formatter, "test_notes")
        print("✅ NotesManager: OK")
        
    except Exception as e:
        print(f"❌ Notes test failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🎓 Enhanced Interactive Learning System - Test Suite")
    print("=" * 60)
    
    # Test components first
    if not test_components():
        print("\n❌ Component tests failed. Enhanced mode may not work properly.")
        return
    
    print("\n✅ All components tested successfully!")
    print("\nChoose test mode:")
    print("1. Test Enhanced Interactive System (full interface)")
    print("2. Quick component test only (already done)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching Enhanced Interactive System Test...")
        test_enhanced_interactive()
    elif choice == "2":
        print("\n✅ Component tests completed!")
    elif choice == "3":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice")

if __name__ == "__main__":
    main()