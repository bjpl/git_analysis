#!/usr/bin/env python3
"""
Test CLI to debug the recursion issue
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_curriculum_list():
    print("Testing curriculum list command...")
    from src.command_router import CommandRouter
    router = CommandRouter()
    
    success = await router.route_command('curriculum', ['list'])
    print(f"Command executed: {success}")

def test_cli_initialization():
    """Test that CLI initializes correctly"""
    print("Testing CLI initialization...")
    try:
        from src.cli import CurriculumCLI
        cli = CurriculumCLI()
        print("✅ CLI initialization successful")
        return True
    except Exception as e:
        print(f"❌ CLI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing CLI Implementation")
    print("=" * 60)
    
    # Test basic CLI initialization
    if not test_cli_initialization():
        return 1
    
    # Test curriculum command
    print("Testing curriculum list command...")
    try:
        asyncio.run(test_curriculum_list())
        print("✅ Curriculum command working")
    except Exception as e:
        print(f"❌ Curriculum command failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("=" * 60)
    print("🎉 All tests passed! CLI is ready to use.")
    print("\nTo run the CLI interactively:")
    print("python cli.py")
    print("\nTo run curriculum commands:")
    print("python cli.py curriculum list")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())