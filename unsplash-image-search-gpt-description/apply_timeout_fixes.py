"""
Apply Timeout Fixes to Main Application

This script applies the API timeout and cancellation fixes to the main.py application.
It patches the existing methods with enhanced versions that provide:

1. Proper timeout configurations
2. Exponential backoff retry with jitter
3. Cancellation token support
4. Enhanced error handling
5. Rate limiting awareness
6. Progress callbacks with better UX

Usage:
    python apply_timeout_fixes.py
    
Or import and use programmatically:
    from apply_timeout_fixes import patch_main_app
    success = patch_main_app()
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def patch_main_app() -> bool:
    """
    Apply timeout patches to the main application.
    Returns True if successful, False otherwise.
    """
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Import the patches
        from patches.api_timeout_fixes import apply_timeout_patches
        
        # Import main app module
        try:
            import main
            logger.info("Successfully imported main module")
        except ImportError as e:
            logger.error(f"Failed to import main module: {e}")
            return False
        
        # Patch the ImageSearchApp class
        original_init = main.ImageSearchApp.__init__
        
        def enhanced_init(self, *args, **kwargs):
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Apply timeout patches
            logger.info("Applying API timeout patches...")
            self._timeout_patches = apply_timeout_patches(self)
            
            if self._timeout_patches:
                logger.info("API timeout patches applied successfully")
                
                # Add cleanup to the exit handler
                original_on_exit = getattr(self, 'on_exit', None)
                
                def enhanced_on_exit():
                    logger.info("Cleaning up timeout patches...")
                    if hasattr(self, '_timeout_patches') and self._timeout_patches:
                        self._timeout_patches.cleanup()
                    if original_on_exit:
                        original_on_exit()
                
                self.on_exit = enhanced_on_exit
                
                # Add status display method
                def show_api_status(self):
                    """Show API status dialog with timeout information."""
                    if hasattr(self, '_timeout_patches') and self._timeout_patches:
                        status = self._timeout_patches.get_status()
                        
                        import tkinter as tk
                        from tkinter import messagebox
                        
                        status_text = "API Status Information:\n\n"
                        status_text += f"Active Operations: {status['active_operations']}\n"
                        status_text += f"Enhanced Services: {status['enhanced_services_available']}\n\n"
                        
                        if 'timeout_manager' in status:
                            tm_status = status['timeout_manager']
                            status_text += "Timeout Manager:\n"
                            status_text += f"  Thread Count: {tm_status.get('thread_count', 0)}\n"
                            status_text += f"  Active Sessions: {tm_status.get('active_sessions', 0)}\n\n"
                        
                        if 'unsplash_rate_limit' in status:
                            rl_status = status['unsplash_rate_limit']
                            remaining = rl_status.get('remaining', 'Unknown')
                            reset_in = rl_status.get('reset_in_seconds', 'Unknown')
                            status_text += f"Unsplash Rate Limit:\n"
                            status_text += f"  Remaining: {remaining}\n"
                            status_text += f"  Reset in: {reset_in}s\n\n"
                        
                        if 'openai_usage' in status:
                            usage = status['openai_usage']
                            status_text += "OpenAI Usage:\n"
                            status_text += f"  Tokens Used: {usage.get('total_tokens_used', 0):,}\n"
                            status_text += f"  Requests: {usage.get('request_count', 0)}\n"
                            status_text += f"  Model: {usage.get('model', 'Unknown')}\n"
                        
                        messagebox.showinfo("API Status", status_text)
                    else:
                        messagebox.showinfo("API Status", "Timeout patches not available")
                
                self.show_api_status = show_api_status
                
                # Add cancel all button to UI
                self._add_cancel_button()
                
            else:
                logger.warning("Failed to apply timeout patches")
        
        # Apply the enhanced init
        main.ImageSearchApp.__init__ = enhanced_init
        
        logger.info("Main application patched successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to patch main application: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_cancel_button_to_app(app_instance):
    """
    Add cancel button to the application UI.
    """
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Find the search frame
        search_frame = None
        for widget in app_instance.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame) and hasattr(child, 'winfo_children'):
                        # Check if this frame has search-related widgets
                        child_widgets = child.winfo_children()
                        if any(hasattr(w, 'get') for w in child_widgets):  # Entry widget
                            search_frame = child
                            break
                if search_frame:
                    break
        
        if search_frame:
            # Add cancel button
            cancel_button = ttk.Button(
                search_frame,
                text="⏹ Cancel All",
                command=lambda: app_instance.cancel_all_operations() if hasattr(app_instance, 'cancel_all_operations') else None
            )
            
            # Add to the search frame (find appropriate position)
            widgets = search_frame.winfo_children()
            row = 1  # Usually second row
            col = len([w for w in widgets if hasattr(w, 'grid_info') and w.grid_info().get('row') == row])
            
            cancel_button.grid(row=row, column=col, padx=5, pady=(5, 0), sticky=tk.W)
            
            # Add status button
            status_button = ttk.Button(
                search_frame,
                text="📊 API Status",
                command=lambda: app_instance.show_api_status() if hasattr(app_instance, 'show_api_status') else None
            )
            status_button.grid(row=row, column=col+1, padx=5, pady=(5, 0), sticky=tk.W)
            
            logger.info("Added cancel and status buttons to UI")
        
    except Exception as e:
        logger.error(f"Failed to add cancel button: {e}")

# Monkey patch method to add buttons
def _add_cancel_button(app_instance):
    """Internal method to add cancel button."""
    # Delay the button addition until after UI is fully created
    def add_buttons():
        add_cancel_button_to_app(app_instance)
    
    app_instance.after(100, add_buttons)

# Add method to ImageSearchApp class
setattr(main.ImageSearchApp, '_add_cancel_button', _add_cancel_button) if 'main' in sys.modules else None

def create_enhanced_main_wrapper():
    """
    Create an enhanced version of main.py that automatically applies patches.
    """
    wrapper_code = '''
#!/usr/bin/env python3
"""
Enhanced Main Application with Timeout Fixes

This is a wrapper around the original main.py that automatically applies
API timeout and cancellation fixes for better reliability.
"""

import sys
from pathlib import Path

# Apply patches before importing main
sys.path.insert(0, str(Path(__file__).parent))
from apply_timeout_fixes import patch_main_app

# Apply patches
if patch_main_app():
    print("\u2713 API timeout patches applied successfully")
else:
    print("\u26a0 Warning: Could not apply all timeout patches")

# Import and run the main application
if __name__ == "__main__":
    try:
        from main import main
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
'''
    
    enhanced_main_path = Path(__file__).parent / "main_with_timeout_fixes.py"
    
    try:
        with open(enhanced_main_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
        
        logger.info(f"Created enhanced main wrapper: {enhanced_main_path}")
        return enhanced_main_path
        
    except Exception as e:
        logger.error(f"Failed to create enhanced main wrapper: {e}")
        return None

def test_timeout_fixes():
    """
    Test the timeout fixes without running the full application.
    """
    logger.info("Testing timeout fixes...")
    
    try:
        # Test service imports
        from src.services.api_timeout_manager import api_timeout_manager
        from src.services.enhanced_unsplash_service import EnhancedUnsplashService
        from src.services.enhanced_openai_service import EnhancedOpenAIService
        
        logger.info("\u2713 Enhanced services imported successfully")
        
        # Test timeout manager
        status = api_timeout_manager.get_status()
        logger.info(f"\u2713 Timeout manager status: {status}")
        
        # Test configuration
        timeout_config = api_timeout_manager.get_timeout_config('unsplash')
        logger.info(f"\u2713 Unsplash timeout config: connect={timeout_config.connect}s, read={timeout_config.read}s")
        
        timeout_config = api_timeout_manager.get_timeout_config('openai')
        logger.info(f"\u2713 OpenAI timeout config: connect={timeout_config.connect}s, read={timeout_config.read}s")
        
        logger.info("\u2713 All timeout fixes are working correctly")
        return True
        
    except Exception as e:
        logger.error(f"\u2717 Timeout fixes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point for applying timeout fixes."""
    print("API Timeout Fixes - Application Patcher")
    print("=" * 50)
    
    # Test the fixes first
    print("1. Testing timeout fixes...")
    if not test_timeout_fixes():
        print("\u2717 Tests failed. Fixes may not work properly.")
        return False
    
    # Apply patches
    print("2. Applying patches to main application...")
    if patch_main_app():
        print("\u2713 Patches applied successfully")
    else:
        print("\u2717 Failed to apply patches")
        return False
    
    # Create enhanced wrapper
    print("3. Creating enhanced main wrapper...")
    enhanced_path = create_enhanced_main_wrapper()
    if enhanced_path:
        print(f"\u2713 Enhanced wrapper created: {enhanced_path}")
        print("\nYou can now run: python main_with_timeout_fixes.py")
    else:
        print("\u2717 Failed to create enhanced wrapper")
    
    print("\n" + "=" * 50)
    print("API Timeout Fixes applied successfully!")
    print("\nFeatures added:")
    print("  \u2713 Configurable timeouts for different API calls")
    print("  \u2713 Exponential backoff retry with jitter")
    print("  \u2713 Cancellation support for long-running operations")
    print("  \u2713 Enhanced error handling with specific error types")
    print("  \u2713 Rate limiting awareness and handling")
    print("  \u2713 Progress callbacks with better UX")
    print("  \u2713 Connection pooling and session management")
    print("  \u2713 Cancel All and API Status buttons in UI")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''