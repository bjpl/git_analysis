#!/usr/bin/env python3
"""
Secure Main Entry Point

Enhanced version of main.py that uses the new secure configuration system.
This replaces the legacy config_manager.py with enterprise-grade security.

Features:
- Zero hardcoded API keys
- Windows DPAPI encryption
- Real-time key validation
- Automatic legacy migration
- First-run setup wizard
"""

import tkinter as tk
from tkinter import messagebox
import sys
import logging
import asyncio
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import (
    SecureConfigManager, 
    ensure_secure_configuration,
    migrate_legacy_configuration
)

# Import the main application
from main import ImageSearchApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SecureImageSearchApp(ImageSearchApp):
    """Enhanced ImageSearchApp with secure configuration management."""
    
    def __init__(self):
        """Initialize the application with secure configuration."""
        
        # Create secure configuration manager
        self.secure_config_manager = SecureConfigManager()
        
        # Check for legacy configuration and migrate if needed
        self._handle_legacy_migration()
        
        # Ensure secure configuration is available
        if self.secure_config_manager.is_first_run():
            self.secure_config_manager = ensure_secure_configuration(None)
            if not self.secure_config_manager:
                # User cancelled setup
                self.quit()
                return
        
        # Validate configuration
        if not self.secure_config_manager.validate_api_keys():
            logger.error("No valid API keys found after configuration")
            messagebox.showerror(
                "Configuration Error",
                "No valid API keys found. Please run the setup wizard."
            )
            self.quit()
            return
        
        # Initialize parent class but skip the old config manager setup
        tk.Tk.__init__(self)
        
        # Replace the old config manager with our secure one
        self._setup_secure_config()
        
        # Continue with normal initialization
        self._init_application()
    
    def _handle_legacy_migration(self):
        """Handle migration from legacy configuration if needed."""
        try:
            # Only attempt migration if no secure config exists
            if self.secure_config_manager.is_first_run():
                logger.info("Checking for legacy configuration to migrate...")
                
                # Run migration in a separate thread to avoid blocking
                migration_result = asyncio.run(
                    migrate_legacy_configuration(self.secure_config_manager)
                )
                
                if migration_result is True:
                    logger.info("Legacy configuration migrated successfully")
                    messagebox.showinfo(
                        "Migration Complete",
                        "Your existing API keys have been migrated to the new secure system.\n\n"
                        "Your keys are now encrypted and stored safely in your user profile."
                    )
                elif migration_result is False:
                    logger.warning("Legacy configuration migration failed")
                else:
                    logger.info("No legacy configuration found")
                    
        except Exception as e:
            logger.error(f"Error during legacy migration: {e}")
            # Continue anyway - migration failure shouldn't prevent app startup
    
    def _setup_secure_config(self):
        """Setup secure configuration to replace legacy config manager."""
        
        # Get API keys from secure configuration
        api_keys = self.secure_config_manager.get_api_keys()
        ui_settings = self.secure_config_manager.get_ui_settings()
        
        # Set up API credentials
        self.UNSPLASH_ACCESS_KEY = api_keys['unsplash']
        self.OPENAI_API_KEY = api_keys['openai']
        self.GPT_MODEL = api_keys['gpt_model']
        
        # Initialize OpenAI client
        from openai import OpenAI
        self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
        
        # Set up paths using secure config directory
        config_info = self.secure_config_manager.get_config_info()
        self.DATA_DIR = Path(config_info['config_dir']) / 'data'
        self.LOG_FILENAME = self.DATA_DIR / 'session_log.json'
        self.CSV_TARGET_WORDS = self.DATA_DIR / 'vocabulary.csv'
        
        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV with headers if it doesn't exist
        if not self.CSV_TARGET_WORDS.exists():
            import csv
            with open(self.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
        
        # Apply UI settings
        self.zoom_level = float(ui_settings.get('zoom_level', 100))
        
        logger.info("Secure configuration loaded successfully")
    
    def _init_application(self):
        """Initialize the application with secure configuration."""
        
        # Initialize application state
        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()
        self.vocabulary_cache = set()
        self.image_cache = {}
        
        # Paging state
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Load cached data
        self.load_used_image_urls_from_log()
        self.load_vocabulary_cache()
        
        # Initialize UI
        from ui.theme_manager import ThemeManager
        self.theme_manager = ThemeManager(self.secure_config_manager)
        self.theme_manager.initialize(self)
        self.theme_manager.register_theme_callback(self.on_theme_change)
        
        # Set up window
        self.title("Secure Unsplash & GPT Tool - Enhanced Security")
        self.geometry("1100x800")
        self.resizable(True, True)
        
        # Initialize UI state
        self.loading_animation_id = None
        
        # Create widgets and setup
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Show API status
        self.update_title_with_status()
        self.load_last_search()
        self.update_stats()
        
        logger.info("Application initialized with secure configuration")
    
    def save_ui_settings(self):
        """Save current UI settings to secure configuration."""
        try:
            ui_settings = {
                'zoom_level': self.zoom_level,
                'theme': self.theme_manager.current_theme if hasattr(self, 'theme_manager') else 'light'
            }
            
            # Note: This would need to be async in a real implementation
            # For now, we'll skip the save to avoid blocking
            logger.info("UI settings would be saved here (async implementation needed)")
            
        except Exception as e:
            logger.error(f"Error saving UI settings: {e}")
    
    def update_title_with_status(self):
        """Update window title with security status."""
        model = self.GPT_MODEL
        theme = self.theme_manager.current_theme.title() if hasattr(self, 'theme_manager') else 'Light'
        encryption_status = "🔒 DPAPI" if self.secure_config_manager.encryption_manager.dpapi_available else "🔒 Encrypted"
        self.title(f"Secure Unsplash & GPT Tool - Model: {model} - Theme: {theme} - {encryption_status}")
    
    def on_exit(self):
        """Enhanced exit handler with secure cleanup."""
        try:
            # Save UI settings
            self.save_ui_settings()
            
            # Save session data
            self.save_session_to_json()
            
            # Log secure shutdown
            logger.info("Application shutting down securely")
            
        except Exception as e:
            logger.error(f"Error during secure shutdown: {e}")
        finally:
            self.destroy()


def main():
    """
    Secure main entry point for the application.
    
    This replaces the original main() function with enhanced security features:
    - Secure configuration management
    - Legacy configuration migration
    - Enhanced error handling
    - Proper logging
    """
    
    try:
        logger.info("Starting secure Unsplash Image Search application")
        
        # Create and run the secure application
        app = SecureImageSearchApp()
        
        # Only run if configuration was successful
        if hasattr(app, 'secure_config_manager') and app.secure_config_manager:
            logger.info("Starting application main loop")
            app.mainloop()
        else:
            logger.warning("Application startup cancelled or failed")
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        
    except Exception as e:
        logger.error(f"Critical application error: {e}", exc_info=True)
        
        # Show error dialog if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Critical Error",
                f"The application encountered a critical error:\n\n{str(e)}\n\n"
                "Please check the log file (app.log) for more details."
            )
            root.destroy()
        except:
            # If even the error dialog fails, just print to console
            print(f"CRITICAL ERROR: {e}")
    
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()