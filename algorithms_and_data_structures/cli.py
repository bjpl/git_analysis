#!/usr/bin/env python3
"""
Algorithms & Data Structures Learning Platform
Enhanced entry point with beautiful CLI formatting
"""

import sys
import os
import argparse
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the beautiful formatter
BeautifulFormatter = None
CLIFormatter = None
formatter = None

try:
    from src.cli_formatter import CLIFormatter, BoxStyle, display_header, display_panel, success, error, info
    formatter = CLIFormatter()
    BEAUTIFUL_CLI = True
    # Create a mock GradientPreset for compatibility
    class GradientPreset:
        CYBERPUNK = "cyberpunk"
        OCEAN = "ocean"
        FOREST = "forest"
        RAINBOW = "rainbow"
        SUNSET = "sunset"
        NEON = "neon"
except ImportError:
    try:
        from src.ui.enhanced_formatter import BeautifulFormatter as BF, GradientPreset
        BeautifulFormatter = BF
        formatter = BF()  # Create instance of BeautifulFormatter
        BEAUTIFUL_CLI = True
    except ImportError:
        BEAUTIFUL_CLI = False
        # Create a mock formatter for fallback
        class MockFormatter:
            def clear_screen(self):
                os.system('cls' if sys.platform == 'win32' else 'clear')
            def ascii_art_banner(self, text):
                return f"=== {text} ==="
            def gradient_text(self, text, preset=None):
                return text
        formatter = MockFormatter()
        class GradientPreset:
            CYBERPUNK = "cyberpunk"
            OCEAN = "ocean"
            FOREST = "forest"
            RAINBOW = "rainbow"
            SUNSET = "sunset"
            NEON = "neon"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Algorithms & Data Structures Learning Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                           # Start in interactive mode
  python cli.py curriculum list           # List all curricula
  python cli.py curriculum show 1         # Show curriculum details
  python cli.py curriculum create         # Create new curriculum
  python cli.py --cloud                  # Start with cloud features
  python cli.py --setup-cloud            # Setup cloud integration
  python cli.py --offline                # Force offline mode
  python cli.py --reset-progress         # Reset learning progress
        """
    )
    
    parser.add_argument(
        '--cloud', 
        action='store_true',
        help='Enable cloud features (sync, challenges, leaderboards)'
    )
    
    parser.add_argument(
        '--offline',
        action='store_true', 
        help='Force offline mode (no cloud features)'
    )
    
    parser.add_argument(
        '--setup-cloud',
        action='store_true',
        help='Run cloud integration setup'
    )
    
    parser.add_argument(
        '--reset-progress',
        action='store_true',
        help='Reset all learning progress'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Show beautiful CLI features demo'
    )
    
    parser.add_argument(
        '--menu',
        action='store_true',
        help='Launch new interactive menu with arrow key navigation'
    )
    
    # Add support for command arguments
    parser.add_argument(
        'command',
        nargs='?',
        help='Command to execute (e.g., curriculum, help)'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='Command arguments'
    )
    
    return parser.parse_args()

async def setup_cloud_integration():
    """Setup cloud integration"""
    try:
        from config.mcp_setup import MCPSetupManager
        
        print("🔧 Setting up Flow Nexus cloud integration...")
        setup_manager = MCPSetupManager()
        success = setup_manager.run_full_setup()
        
        if success:
            print("\n✅ Cloud integration setup completed!")
            print("You can now use --cloud flag to enable cloud features")
        else:
            print("\n⚠️ Setup completed with warnings")
            print("Some features may not be available")
        
        return success
        
    except ImportError:
        print("❌ Setup module not found")
        return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

async def main():
    """Enhanced main entry point with beautiful CLI"""
    args = parse_arguments()
    
    # Initialize beautiful formatter if available
    global formatter
    if BEAUTIFUL_CLI and BeautifulFormatter and not formatter:
        formatter = BeautifulFormatter()
    
    try:
        # Handle special commands first
        if args.menu:
            # Launch the new interactive menu system
            from src.main_menu import MainMenuSystem
            menu_system = MainMenuSystem()
            print(menu_system.formatter.header("🎓 Welcome to Algorithm Learning Platform!", level=1))
            print(menu_system.formatter.info("Master algorithms and data structures with interactive learning"))
            print(menu_system.formatter.success("Now with arrow key navigation! Use ↑↓ or number keys."))
            input("\nPress Enter to start...")
            await menu_system.run()
            return
        
        if args.demo and BEAUTIFUL_CLI:
            # Show beautiful CLI demo
            from src.ui.enhanced_formatter import demo_beautiful_cli
            demo_beautiful_cli()
            return
        
        if args.setup_cloud:
            await setup_cloud_integration()
            return
        
        # Handle command-line commands (non-interactive mode)
        if args.command:
            from src.command_router import CommandRouter
            router = CommandRouter()
            
            # Build command arguments
            command_args = [args.command] + (args.args or [])
            command, remaining_args = router.parse_command(command_args)
            
            # Route the command
            success = await router.route_command(command, remaining_args)
            sys.exit(0 if success else 1)
        
        # Import the enhanced CLI after path setup
        from src.enhanced_cli import EnhancedCLI
        
        # Show beautiful startup message
        if BEAUTIFUL_CLI:
            formatter.clear_screen()
            
            # Beautiful ASCII banner with gradient
            banner = formatter.ascii_art_banner("ALGORITHMS")
            print(formatter.gradient_text(banner, GradientPreset.CYBERPUNK))
            
            # Mode-specific messages with beautiful formatting
            if args.cloud:
                title = formatter.gradient_text(
                    "☁️ Cloud-Enhanced Learning Platform",
                    GradientPreset.OCEAN
                )
                print(f"\n{title}")
                features = [
                    "Real-time sync across devices",
                    "Global challenges & competitions",
                    "Live leaderboards",
                    "Collaborative learning"
                ]
                for feature in features:
                    print(f"  {formatter.status_icon('star')} {feature}")
            elif args.offline:
                title = formatter.gradient_text(
                    "📚 Offline Learning Mode",
                    GradientPreset.FOREST
                )
                print(f"\n{title}")
                features = [
                    "Complete curriculum access",
                    "Local progress tracking",
                    "Personal notes system",
                    "No internet required"
                ]
                for feature in features:
                    print(f"  {formatter.status_icon('success')} {feature}")
            else:
                title = formatter.gradient_text(
                    "Your Journey to Mastery Begins Here!",
                    GradientPreset.RAINBOW
                )
                print(f"\n{title}")
                subtitle = formatter.gradient_text(
                    "Master algorithms & data structures with interactive learning",
                    GradientPreset.SUNSET
                )
                print(subtitle)
            
            # Beautiful separator
            print("\n" + formatter.gradient_text("═" * 70, GradientPreset.NEON))
        else:
            # Fallback to simple messages
            if args.cloud:
                print("🎓 Starting Algorithms & Data Structures Learning Platform (Cloud Mode)...")
                print("☁️ Cloud features: sync, challenges, leaderboards, collaboration")
            elif args.offline:
                print("🎓 Starting Algorithms & Data Structures Learning Platform (Offline Mode)...")
                print("📱 Local-only features: progress tracking, notes, curriculum")
            else:
                print("🎓 Starting Algorithms & Data Structures Learning Platform...")
                print("Your comprehensive guide to mastering computer science fundamentals")
        
        print()
        
        # Initialize CLI with appropriate settings
        cli_options = {
            'reset_progress': args.reset_progress,
            'cloud_mode': args.cloud,
            'offline_mode': args.offline,
            'debug_mode': args.debug,
            'config_path': args.config
        }
        
        cli = EnhancedCLI(**cli_options)
        
        # Initialize cloud integration if requested
        if args.cloud:
            await cli.initialize_cloud_features()
        
        # Run the CLI
        await cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 Exiting... See you next time!")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        if args.cloud:
            print("For cloud features, also run: python cli.py --setup-cloud")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        print("Please check your installation and try again.")
        sys.exit(1)

def sync_main():
    """Synchronous wrapper for main function"""
    asyncio.run(main())

if __name__ == '__main__':
    sync_main()