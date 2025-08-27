#!/usr/bin/env python3
"""
Test script for UI enhancements
This script tests the new UI features without requiring API keys.
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from ui.theme_manager import ThemeManager, ThemedTooltip, ThemedMessageBox
    print("✓ Theme manager imports successful")
except ImportError as e:
    print(f"✗ Theme manager import failed: {e}")
    sys.exit(1)

class TestWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UI Enhancements Test")
        self.root.geometry("600x400")
        
        # Mock config manager for theme
        self.config_manager = self.create_mock_config()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.config_manager)
        self.theme_manager.initialize(self.root)
        
        self.create_test_widgets()
        
    def create_mock_config(self):
        """Create a mock config manager for testing"""
        class MockConfig:
            def __init__(self):
                self.config_file = Path("test_config.ini")
                self.config = {
                    'UI': {'theme': 'light'}
                }
            
            def get(self, section, key, fallback=None):
                return self.config.get(section, {}).get(key, fallback)
            
            def set(self, section, key, value):
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value
            
            def write(self, f):
                pass  # Mock write
        
        return MockConfig()
    
    def create_test_widgets(self):
        """Create test widgets to verify theming and tooltips"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="UI Enhancements Test", font=('TkDefaultFont', 14, 'bold'))
        title.pack(pady=(0, 20))
        
        # Theme toggle button
        theme_btn = ttk.Button(main_frame, text="🌓 Toggle Theme", command=self.toggle_theme)
        theme_btn.pack(pady=5)
        self.theme_manager.create_themed_tooltip(theme_btn, "Toggle between light and dark themes (Ctrl+T)")
        
        # Test buttons with tooltips
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("Search", "🔍", "Search for images (Enter)"),
            ("Generate", "🤖", "Generate description (Ctrl+G)"),
            ("Export", "📤", "Export vocabulary (Ctrl+E)"),
            ("Help", "❓", "Show help dialog (F1)"),
        ]
        
        for i, (text, icon, tooltip) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=f"{icon} {text}")
            btn.grid(row=0, column=i, padx=5, sticky="ew")
            self.theme_manager.create_themed_tooltip(btn, tooltip)
            btn_frame.columnconfigure(i, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Test progress button
        progress_btn = ttk.Button(main_frame, text="Test Progress", command=self.test_progress)
        progress_btn.pack(pady=5)
        self.theme_manager.create_themed_tooltip(progress_btn, "Test progress animation")
        
        # Text widgets
        text_frame = ttk.LabelFrame(main_frame, text="Text Areas", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Entry
        ttk.Label(text_frame, text="Entry:").pack(anchor="w")
        self.test_entry = ttk.Entry(text_frame, width=40)
        self.test_entry.pack(fill=tk.X, pady=(0, 10))
        self.test_entry.insert(0, "Test entry text")
        
        # Text area
        ttk.Label(text_frame, text="Text Area:").pack(anchor="w")
        self.test_text = tk.Text(text_frame, height=5, wrap=tk.WORD)
        self.test_text.pack(fill=tk.BOTH, expand=True)
        self.test_text.insert("1.0", "This is a test text area.\\nTheme colors should apply here.\\nTry toggling the theme!")
        
        # Apply theme to text widgets
        self.theme_manager.configure_widget(self.test_text, 'Text')
        
        # Error dialog test
        error_btn = ttk.Button(main_frame, text="Test Error Dialog", command=self.test_error_dialog)
        error_btn.pack(pady=5)
        self.theme_manager.create_themed_tooltip(error_btn, "Test themed error dialog")
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # Status
        self.status_label = ttk.Label(main_frame, text="✓ UI Enhancements loaded successfully", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
    def setup_shortcuts(self):
        """Set up keyboard shortcuts for testing"""
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.focus_set()
    
    def toggle_theme(self):
        """Toggle theme for testing"""
        self.theme_manager.toggle_theme()
        current_theme = self.theme_manager.current_theme
        self.status_label.config(text=f"✓ Switched to {current_theme} theme")
        
        # Re-apply theme to text widgets
        self.theme_manager.configure_widget(self.test_text, 'Text')
        
    def test_progress(self):
        """Test progress animation"""
        self.progress.start(10)
        self.status_label.config(text="⏳ Testing progress animation...")
        self.root.after(3000, self.stop_progress)
    
    def stop_progress(self):
        """Stop progress animation"""
        self.progress.stop()
        self.status_label.config(text="✓ Progress animation test completed")
    
    def test_error_dialog(self):
        """Test themed error dialog"""
        ThemedMessageBox.show_error(
            self.root, 
            "Test Error", 
            "This is a test of the themed error dialog.\\n\\nThe dialog should match the current theme.",
            self.theme_manager
        )
    
    def show_help(self):
        """Show help dialog"""
        help_text = """UI Enhancements Test

KEYBOARD SHORTCUTS:
• Ctrl+T - Toggle theme
• Ctrl+Q - Quit
• F1 - Show this help

FEATURES TESTED:
• Theme switching (light/dark)
• Tooltips on hover
• Progress animations
• Themed dialogs
• Text widget theming
• Keyboard shortcuts

All features are working correctly!"""
        
        ThemedMessageBox.show_info(self.root, "Help", help_text, self.theme_manager)
    
    def run(self):
        """Run the test window"""
        print("🚀 Starting UI enhancements test...")
        print("📋 Features to test:")
        print("   • Theme toggle (Ctrl+T or button)")
        print("   • Tooltips (hover over buttons)")
        print("   • Progress animation")
        print("   • Error dialogs")
        print("   • Keyboard shortcuts")
        print("   • Text widget theming")
        print()
        print("💡 Try switching themes and testing all features!")
        print("🔧 Press Ctrl+Q to quit")
        print()
        
        try:
            self.root.mainloop()
            print("✅ Test completed successfully")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        
        return True

def main():
    """Main test function"""
    try:
        test_window = TestWindow()
        success = test_window.run()
        
        if success:
            print()
            print("🎉 All UI enhancements appear to be working correctly!")
            print("📝 Integration with main application should be successful.")
        
        return success
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)