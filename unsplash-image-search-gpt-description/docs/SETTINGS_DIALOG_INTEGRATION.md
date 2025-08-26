# Settings Dialog Integration Guide

This guide shows how to integrate the comprehensive Settings Dialog into your application.

## Features

The Settings Dialog provides a tabbed interface with the following configuration options:

### 1. API Keys Tab
- **Unsplash Access Key**: Editable field with show/hide toggle
- **OpenAI API Key**: Editable field with show/hide toggle  
- **Direct links**: Quick access to API key registration pages
- **Real-time validation**: Immediate feedback on key format
- **Auto-save**: Keys are saved immediately on change

### 2. GPT Settings Tab
- **Model Selection**: Dropdown with gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
- **Temperature Slider**: 0.0 to 2.0 range for creativity control
- **Max Tokens**: Spinbox for response length (100-2000 tokens)
- **Cost Information**: Displays estimated cost per description
- **Real-time Preview**: Shows current parameter values

### 3. Learning Tab
- **Description Style**: Simple, Detailed, or Poetic generation styles
- **Vocabulary Level**: Beginner, Intermediate, Advanced, Native complexity
- **Adaptive Learning**: Toggle for learning from user feedback
- **Style Descriptions**: Helpful explanations for each option

### 4. Appearance Tab
- **Theme Selection**: Light, Dark, or Auto theme options
- **Font Size**: Slider from 8pt to 24pt with live preview
- **Window Opacity**: Transparency control (50-100%)
- **Live Preview**: See font changes immediately

## Integration Steps

### 1. Basic Integration

```python
import tkinter as tk
from config_manager import ConfigManager
from src.ui.dialogs.settings_menu import show_settings_dialog

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        
        # Add settings menu item
        menubar = tk.Menu(self.root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(
            label="Preferences...", 
            command=self.open_settings
        )
        menubar.add_cascade(label="Settings", menu=settings_menu)
        self.root.config(menu=menubar)
    
    def open_settings(self):
        # Open settings dialog
        dialog = show_settings_dialog(self.root, self.config_manager)
        
        # Optionally refresh UI after settings change
        self.root.after(100, self.refresh_ui_from_settings)
    
    def refresh_ui_from_settings(self):
        # Reload configuration and update UI
        # This is where you'd apply theme changes, font sizes, etc.
        pass
```

### 2. Advanced Integration with Event Handling

```python
from src.ui.dialogs.settings_menu import SettingsDialog

class AdvancedIntegration:
    def open_settings_with_callback(self):
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        # Apply any UI changes based on new settings
        self.apply_appearance_settings()
        self.apply_gpt_settings()
    
    def apply_appearance_settings(self):
        config = self.config_manager.config
        
        if config.has_section('UI'):
            # Apply theme
            theme = config.get('UI', 'theme', fallback='light')
            self.apply_theme(theme)
            
            # Apply font size
            font_size = config.getint('UI', 'font_size', fallback=12)
            self.apply_font_size(font_size)
            
            # Apply opacity
            opacity = config.getfloat('UI', 'opacity', fallback=1.0)
            self.root.wm_attributes('-alpha', opacity)
    
    def apply_gpt_settings(self):
        config = self.config_manager.config
        
        if config.has_section('GPT'):
            temperature = config.getfloat('GPT', 'temperature', fallback=0.7)
            max_tokens = config.getint('GPT', 'max_tokens', fallback=500)
            
            # Update your GPT service configuration
            self.gpt_service.update_parameters(
                temperature=temperature,
                max_tokens=max_tokens
            )
```

### 3. Keyboard Shortcuts

```python
def setup_keyboard_shortcuts(self):
    # Ctrl+, for settings (common shortcut)
    self.root.bind('<Control-comma>', lambda e: self.open_settings())
    
    # F12 for settings (alternative)
    self.root.bind('<F12>', lambda e: self.open_settings())
```

## Configuration Structure

The dialog automatically creates and manages these configuration sections:

```ini
[API]
unsplash_access_key = your_key_here
openai_api_key = your_key_here
gpt_model = gpt-4o-mini

[GPT]
temperature = 0.7
max_tokens = 500

[Learning]
description_style = Simple
vocabulary_level = Beginner
enable_learning = true

[UI]
theme = light
font_size = 12
opacity = 1.0
window_width = 1100
window_height = 800
```

## Event Handling

The dialog provides several ways to handle setting changes:

### 1. Immediate Save (Default)
All changes are saved immediately to `config.ini` when modified.

### 2. Apply Button
Users can make multiple changes and apply them all at once.

### 3. Cancel Support
Users can cancel changes, which restores the original configuration.

### 4. Reset to Defaults
Provides a way to reset all settings to default values (preserves API keys).

## Error Handling

The dialog includes comprehensive error handling:

```python
try:
    dialog = show_settings_dialog(parent, config_manager)
except Exception as e:
    messagebox.showerror("Settings Error", f"Cannot open settings: {e}")
```

## Validation Features

- **API Key Format**: Validates key format and length
- **Parameter Ranges**: Ensures values are within acceptable ranges
- **Real-time Feedback**: Shows validation status as user types
- **Visual Indicators**: Green checkmarks for valid inputs, red errors for invalid

## Accessibility Features

- **Keyboard Navigation**: Full keyboard support with Tab navigation
- **Tooltips**: Helpful explanations for complex settings
- **Clear Labels**: Descriptive labels for all controls
- **Consistent Layout**: Standard dialog patterns for familiarity

## Testing

Run the demo application to test the dialog:

```bash
python examples/settings_dialog_demo.py
```

## File Structure

```
src/ui/dialogs/
├── __init__.py              # Module exports
├── settings_menu.py         # Main settings dialog
├── setup_wizard.py          # Initial setup dialog
└── enhanced_setup_wizard.py # Enhanced setup dialog

examples/
└── settings_dialog_demo.py  # Integration demo

docs/
└── SETTINGS_DIALOG_INTEGRATION.md  # This guide
```

## Dependencies

The settings dialog requires:
- `tkinter` (standard library)
- `configparser` (standard library) 
- `pathlib` (standard library)
- Your application's `ConfigManager` class

## Best Practices

1. **Always use ConfigManager**: Don't bypass the configuration system
2. **Handle errors gracefully**: Wrap dialog calls in try-catch blocks
3. **Refresh UI after changes**: Apply appearance changes immediately
4. **Provide keyboard shortcuts**: Make settings easily accessible
5. **Test thoroughly**: Ensure all settings work as expected
6. **Document custom settings**: If you add new sections, document them

## Customization

The dialog is designed to be easily extensible:

### Adding New Tabs

```python
def _create_custom_tab(self):
    tab_frame = ttk.Frame(self.notebook, padding="15")
    self.notebook.add(tab_frame, text="Custom Settings")
    
    # Add your custom controls here
    # Remember to implement save/load methods
```

### Adding New Settings

```python
# Add to _init_variables()
self.custom_setting_var = tk.StringVar(value="default")

# Add to _load_settings()
if config.has_section('Custom'):
    self.custom_setting_var.set(
        config.get('Custom', 'custom_setting', fallback='default')
    )

# Add to save method
def _save_custom_settings(self):
    config = self.config_manager.config
    if not config.has_section('Custom'):
        config.add_section('Custom')
    
    config.set('Custom', 'custom_setting', self.custom_setting_var.get())
    self._save_config()
```

This comprehensive settings dialog provides a professional, user-friendly way to configure all aspects of your application while maintaining compatibility with the existing ConfigManager system.