"""
Demo script showing how to integrate the Settings Dialog into an application.
This example shows proper usage of the SettingsDialog with ConfigManager integration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from config_manager import ConfigManager
    from src.ui.dialogs.settings_menu import show_settings_dialog
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)


class SettingsDemo:
    """Demo application showing Settings Dialog integration."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Settings Dialog Demo")
        self.root.geometry("600x400")
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        self.create_ui()
        
    def create_ui(self):
        """Create the demo interface."""
        # Title
        title_label = ttk.Label(
            self.root,
            text="Settings Dialog Integration Demo",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Description
        description = ttk.Label(
            self.root,
            text="This demo shows how to integrate the Settings Dialog with your application.\n"
                 "The dialog provides a comprehensive interface for configuring:\n"
                 "• API Keys (Unsplash & OpenAI) with show/hide functionality\n"
                 "• GPT Settings (model, temperature, max tokens)\n"
                 "• Learning preferences (style, vocabulary level)\n"
                 "• Appearance settings (theme, font size, opacity)\n\n"
                 "All changes are saved immediately to config.ini",
            justify=tk.CENTER,
            wraplength=550
        )
        description.pack(pady=20)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=30)
        
        # Open Settings button
        settings_button = ttk.Button(
            buttons_frame,
            text="Open Settings Dialog",
            command=self.open_settings,
            style="Accent.TButton"
        )
        settings_button.pack(side=tk.LEFT, padx=10)
        
        # Show Current Config button
        config_button = ttk.Button(
            buttons_frame,
            text="Show Current Config",
            command=self.show_config
        )
        config_button.pack(side=tk.LEFT, padx=10)
        
        # Reload Config button
        reload_button = ttk.Button(
            buttons_frame,
            text="Reload Config",
            command=self.reload_config
        )
        reload_button.pack(side=tk.LEFT, padx=10)
        
        # Status frame
        self.status_frame = ttk.LabelFrame(self.root, text="Current Configuration", padding=10)
        self.status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Status text with scrollbar
        text_frame = ttk.Frame(self.status_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            font=('Consolas', 10)
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial config display
        self.show_config()
        
        # Configure styles for better appearance
        self.configure_styles()
    
    def configure_styles(self):
        """Configure custom styles for the demo."""
        style = ttk.Style()
        
        # Try to set a modern theme
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure accent button style
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#0078d4",
            focuscolor="none"
        )
        
        # Handle theme-specific configurations
        try:
            style.map(
                "Accent.TButton",
                background=[('active', '#106ebe'), ('pressed', '#005a9e')]
            )
        except tk.TclError:
            pass  # Ignore if style mapping fails
    
    def open_settings(self):
        """Open the settings dialog."""
        try:
            dialog = show_settings_dialog(self.root, self.config_manager)
            
            # Update display after dialog is closed
            self.root.after(100, self.show_config)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to open settings dialog:\n{str(e)}",
                parent=self.root
            )
    
    def show_config(self):
        """Display current configuration."""
        try:
            self.status_text.delete(1.0, tk.END)
            
            # Get API keys
            api_keys = self.config_manager.get_api_keys()
            
            # Build config display
            config_text = "=== CURRENT CONFIGURATION ===\n\n"
            
            # API Configuration
            config_text += "[API KEYS]\n"
            config_text += f"Unsplash Key: {'*' * 20 if api_keys.get('unsplash') else '(not set)'}\n"
            config_text += f"OpenAI Key: {'*' * 20 if api_keys.get('openai') else '(not set)'}\n"
            config_text += f"GPT Model: {api_keys.get('gpt_model', 'gpt-4o-mini')}\n\n"
            
            # Other sections
            config = self.config_manager.config
            
            for section_name in config.sections():
                if section_name == 'API':
                    continue  # Already displayed above
                
                config_text += f"[{section_name.upper()}]\n"
                for key, value in config[section_name].items():
                    config_text += f"{key}: {value}\n"
                config_text += "\n"
            
            # Configuration file location
            config_text += f"Config file: {self.config_manager.config_file}\n"
            config_text += f"Data directory: {self.config_manager.data_dir}\n"
            
            self.status_text.insert(1.0, config_text)
            
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, f"Error loading configuration: {str(e)}")
    
    def reload_config(self):
        """Reload configuration from file."""
        try:
            # Recreate config manager to reload from file
            self.config_manager = ConfigManager()
            self.show_config()
            messagebox.showinfo(
                "Configuration Reloaded",
                "Configuration has been reloaded from file.",
                parent=self.root
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to reload configuration:\n{str(e)}",
                parent=self.root
            )
    
    def run(self):
        """Run the demo application."""
        # Set up window closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show usage instructions
        self.show_instructions()
        
        # Start the GUI
        self.root.mainloop()
    
    def show_instructions(self):
        """Show usage instructions."""
        instructions = (
            "Settings Dialog Demo Instructions:\n\n"
            "1. Click 'Open Settings Dialog' to access all configuration options\n"
            "2. The dialog has 4 tabs:\n"
            "   • API Keys: Configure Unsplash & OpenAI keys\n"
            "   • GPT Settings: Adjust model parameters\n"
            "   • Learning: Set description preferences\n"
            "   • Appearance: Customize UI appearance\n\n"
            "3. All changes are saved immediately to config.ini\n"
            "4. Use 'Show Current Config' to view current settings\n"
            "5. Use 'Reload Config' to refresh from file\n\n"
            "The settings dialog is fully self-contained and can be integrated\n"
            "into any Tkinter application with ConfigManager support."
        )
        
        messagebox.showinfo(
            "Demo Instructions",
            instructions,
            parent=self.root
        )
    
    def on_closing(self):
        """Handle application closing."""
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point."""
    try:
        print("Starting Settings Dialog Demo...")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        
        demo = SettingsDemo()
        demo.run()
        
    except Exception as e:
        print(f"Error starting demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()