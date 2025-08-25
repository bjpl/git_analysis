"""
Demonstration of non-blocking configuration manager.
Shows how the main application window remains responsive while the setup wizard is displayed.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from config_manager_fix import ensure_api_keys_configured_async, ConfigManager


class DemoApp:
    """Demo application to show non-blocking configuration."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Non-Blocking Config Demo")
        self.root.geometry("500x400")
        
        self.config_manager = None
        self.setup_ui()
        self.start_background_tasks()
        
        # Try to configure API keys asynchronously
        self.check_config_async()
    
    def setup_ui(self):
        """Create the demo UI."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Non-Blocking Configuration Demo",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Status display
        self.status_text = tk.Text(main_frame, height=15, width=60)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Test buttons to show the app remains responsive
        ttk.Button(
            button_frame,
            text="Show Config Wizard",
            command=self.show_config_wizard
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Check API Keys",
            command=self.check_api_keys
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Counter to show the app is not frozen
        self.counter = 0
        self.counter_label = ttk.Label(main_frame, text="Counter: 0")
        self.counter_label.pack(pady=(10, 0))
        
        self.log("Demo application started")
        self.log("The application remains responsive even when setup wizard is shown")
    
    def log(self, message):
        """Add message to status log."""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the status log."""
        self.status_text.delete(1.0, tk.END)
    
    def check_config_async(self):
        """Check configuration asynchronously."""
        self.log("Checking API configuration...")
        
        def config_callback(result, config_manager):
            """Handle configuration result."""
            if result is True:
                self.config_manager = config_manager
                self.log("✓ API keys are configured and valid")
                keys = config_manager.get_api_keys()
                self.log(f"Using GPT model: {keys['gpt_model']}")
            elif result == 'skipped':
                self.log("⚠ API setup was skipped - you can configure later")
                self.config_manager = config_manager
            else:
                self.log("✗ API setup was cancelled")
        
        # This call is non-blocking - the main window remains responsive
        result = ensure_api_keys_configured_async(self.root, config_callback)
        
        if result:  # Keys were already configured
            self.config_manager = result
            self.log("✓ API keys were already configured")
    
    def show_config_wizard(self):
        """Manually show the configuration wizard."""
        self.log("Opening configuration wizard...")
        
        def config_callback(result, config_manager):
            """Handle manual configuration result."""
            if result is True:
                self.config_manager = config_manager
                self.log("✓ Configuration updated successfully")
            elif result == 'skipped':
                self.log("Configuration setup skipped")
            else:
                self.log("Configuration cancelled")
        
        # Show wizard even if keys are already configured
        from config_manager_fix import NonBlockingSetupWizard
        config = ConfigManager()
        wizard = NonBlockingSetupWizard(self.root, config, config_callback)
    
    def check_api_keys(self):
        """Check current API key status."""
        if not self.config_manager:
            self.config_manager = ConfigManager()
        
        if self.config_manager.validate_api_keys():
            keys = self.config_manager.get_api_keys()
            self.log("✓ API keys are configured:")
            self.log(f"  - Unsplash: {keys['unsplash'][:8]}..." if keys['unsplash'] else "  - Unsplash: Not set")
            self.log(f"  - OpenAI: {keys['openai'][:8]}..." if keys['openai'] else "  - OpenAI: Not set")
            self.log(f"  - GPT Model: {keys['gpt_model']}")
        else:
            self.log("✗ API keys are not properly configured")
    
    def start_background_tasks(self):
        """Start background tasks to show the app is responsive."""
        def update_counter():
            """Update counter every second to show app is not frozen."""
            self.counter += 1
            self.counter_label.config(text=f"Counter: {self.counter}")
            # Schedule next update
            self.root.after(1000, update_counter)
        
        # Start the counter
        update_counter()
    
    def run(self):
        """Run the demo application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()


if __name__ == "__main__":
    demo = DemoApp()
    demo.run()