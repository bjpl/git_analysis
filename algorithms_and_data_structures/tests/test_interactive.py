#!/usr/bin/env python3
"""
Test interactive mode curriculum commands
"""

import sys
import asyncio
import io
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_interactive_curriculum_commands():
    """Test curriculum commands in interactive mode"""
    print("Testing interactive mode curriculum commands...")
    
    try:
        from src.enhanced_cli import EnhancedCLI
        
        # Create CLI instance
        cli = EnhancedCLI()
        print("✅ CLI created successfully")
        
        # Test curriculum command handler
        print("Testing _handle_curriculum_command...")
        
        # Test in async context
        async def run_test():
            await cli._handle_curriculum_command("curriculum list")
            return True
        
        result = asyncio.run(run_test())
        print("✅ Interactive curriculum command executed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_recognition():
    """Test if curriculum commands are recognized"""
    print("Testing command recognition...")
    
    try:
        from src.enhanced_cli import EnhancedCLI
        cli = EnhancedCLI()
        
        test_commands = [
            "curriculum list",
            "curr list", 
            "curriculum show 1",
            "curr-list"
        ]
        
        for cmd in test_commands:
            is_curriculum_cmd = cli._is_curriculum_command(cmd)
            print(f"  '{cmd}' -> {is_curriculum_cmd}")
            if not is_curriculum_cmd:
                print(f"❌ Command '{cmd}' not recognized as curriculum command")
                return False
        
        print("✅ All curriculum commands recognized correctly")
        return True
        
    except Exception as e:
        print(f"❌ Command recognition test failed: {e}")
        return False

def main():
    """Run interactive tests"""
    print("🧪 Testing Interactive Mode Curriculum Integration")
    print("=" * 60)
    
    tests = [
        test_command_recognition,
        test_interactive_curriculum_commands
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Interactive tests: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("🎉 Interactive mode curriculum integration working!")
        print("\nYou can now use curriculum commands in interactive mode:")
        print("  - C1: List curricula")
        print("  - C2: Show curriculum details")
        print("  - Or type commands directly like 'curriculum list'")
    else:
        print("❌ Some interactive tests failed")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())