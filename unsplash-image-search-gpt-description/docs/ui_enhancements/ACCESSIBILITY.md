# Accessibility Implementation Guide

This document provides comprehensive guidance on the accessibility features implemented in the Unsplash Image Search application.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Getting Started](#getting-started)
4. [Configuration](#configuration)
5. [Keyboard Navigation](#keyboard-navigation)
6. [Screen Reader Support](#screen-reader-support)
7. [Visual Accessibility](#visual-accessibility)
8. [Audio Feedback](#audio-feedback)
9. [Development Guide](#development-guide)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)

## Overview

The application implements comprehensive accessibility features to ensure WCAG 2.1 AA compliance and provide an inclusive user experience for users with disabilities. The accessibility system is built around several key components:

- **AccessibilityManager**: Central coordinator for all accessibility features
- **ScreenReaderSupport**: Text-to-speech and screen reader integration  
- **FocusManager**: Enhanced focus indicators and tab order management
- **KeyboardNavigation**: Comprehensive keyboard shortcuts and navigation
- **AccessibilityThemes**: High contrast and color blind friendly themes
- **SoundManager**: Audio cues and feedback system

## Features

### Core Accessibility Features

✅ **Screen Reader Support**
- Text-to-speech announcements
- Integration with NVDA, JAWS, VoiceOver, and Orca
- Configurable announcement verbosity
- Live region updates

✅ **Keyboard Navigation**
- Complete keyboard-only operation
- Customizable keyboard shortcuts
- Arrow key navigation in lists and grids
- Tab order management

✅ **Visual Accessibility**
- High contrast themes (4 variants)
- Color blind friendly themes (3 types)
- Font size scaling (50% to 200%)
- Enhanced focus indicators

✅ **Audio Feedback**
- Sound cues for user actions
- Contextual audio feedback
- Volume control and disable option
- Cross-platform audio support

✅ **ARIA-like Attributes**
- Accessible names and descriptions
- Role definitions for widgets
- State and property management
- Live region announcements

### Supported Assistive Technologies

| Technology | Platform | Support Level |
|------------|----------|---------------|
| NVDA | Windows | Full |
| JAWS | Windows | Full |
| Windows Narrator | Windows | Partial |
| VoiceOver | macOS | Full |
| Orca | Linux | Partial |
| Built-in TTS | All | Full |

## Getting Started

### Basic Setup

1. **Enable Accessibility Features**
   ```python
   from src.ui.accessibility import AccessibilityManager
   
   # Initialize accessibility manager
   accessibility = AccessibilityManager(root_window)
   
   # Make widgets accessible
   accessible_button = accessibility.make_accessible(
       button,
       name="Search Images",
       description="Search for images on Unsplash",
       role="button"
   )
   ```

2. **Quick Settings**
   - Press `Ctrl+Alt+S` to open accessibility settings
   - Press `Ctrl+Alt+H` to toggle high contrast mode
   - Press `Ctrl+Plus/Minus` to adjust font size
   - Press `F1` on any widget for help

### First-Time Users

For users new to the application:

1. **Screen Reader Users**: The application will announce navigation and provide audio feedback
2. **Keyboard Users**: Use Tab/Shift+Tab to navigate, Enter/Space to activate
3. **Low Vision Users**: Enable high contrast mode and adjust font size as needed
4. **Motor Impairments**: Customize keyboard shortcuts and use focus indicators

## Configuration

### Accessibility Settings Panel

Access via `Ctrl+Alt+S` or the accessibility menu. The panel contains five tabs:

#### Display Tab
- **Font Size**: Scale from 50% to 200% using slider or preset buttons
- **High Contrast**: Choose from 4 high contrast themes
- **Color Blind Mode**: Support for deuteranopia, protanopia, and tritanopia
- **Reduced Motion**: Minimize animations and transitions

#### Navigation Tab
- **Keyboard Navigation**: Enable/disable keyboard navigation
- **Focus Indicators**: Customize focus ring appearance
- **Tab Order**: View and modify widget tab order

#### Audio Tab
- **Sound Cues**: Enable audio feedback for actions
- **Screen Reader**: Configure text-to-speech settings
- **Announcement Level**: Choose verbosity (quiet, normal, verbose)

#### Shortcuts Tab
- **View Current Shortcuts**: See all keyboard shortcuts
- **Customize Shortcuts**: Change key combinations
- **Reset to Defaults**: Restore original shortcuts

#### Advanced Tab
- **System Integration**: Detect OS accessibility settings
- **Import/Export**: Save and share accessibility configurations
- **Diagnostics**: Test accessibility features and detect issues

### Configuration Files

Settings are automatically saved to:
- **Windows**: `%USERPROFILE%\.accessibility_settings.json`
- **macOS**: `~/.accessibility_settings.json`
- **Linux**: `~/.accessibility_settings.json`

Example configuration:
```json
{
  "font_scale": 1.2,
  "high_contrast": true,
  "color_blind_mode": "deuteranopia",
  "sound_enabled": true,
  "focus_indicators": true,
  "keyboard_navigation": true,
  "screen_reader_enabled": true,
  "reduced_motion": false,
  "announcement_verbosity": "normal",
  "custom_shortcuts": {
    "toggle_high_contrast": "<Control-Alt-h>",
    "increase_font": "<Control-plus>"
  }
}
```

## Keyboard Navigation

### Global Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+Alt+A` | Accessibility Help | Show help dialog |
| `Ctrl+Alt+S` | Accessibility Settings | Open settings panel |
| `Ctrl+Alt+H` | Toggle High Contrast | Switch theme |
| `Ctrl+Plus` | Increase Font | Make text larger |
| `Ctrl+Minus` | Decrease Font | Make text smaller |
| `Ctrl+0` | Reset Font | Return to 100% |
| `F1` | Context Help | Help for current widget |

### Navigation Keys

| Key | Action | Context |
|-----|--------|---------|
| `Tab` | Next Element | All contexts |
| `Shift+Tab` | Previous Element | All contexts |
| `Arrow Keys` | Navigate Lists/Grids | Lists, trees, tabs |
| `Home` | First Element | Lists, containers |
| `End` | Last Element | Lists, containers |
| `Page Up/Down` | Scroll/Section | Scrollable areas |
| `Enter` | Activate | Buttons, links |
| `Space` | Toggle/Activate | Checkboxes, buttons |
| `Escape` | Cancel/Close | Dialogs, menus |

### Screen Reader Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Alt+R` | Read Current Widget |
| `Ctrl+Alt+N` | Read Next Widget |
| `Ctrl+Alt+P` | Read Previous Widget |

### Application-Specific Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Search |
| `Ctrl+G` | Generate Description |
| `Ctrl+E` | Export Vocabulary |
| `Ctrl+T` | Toggle Theme |

## Screen Reader Support

### Announcements

The application provides contextual announcements for:

- **Navigation**: "Button, Search Images, Press Enter to activate"
- **Actions**: "Image loaded successfully"
- **Status**: "Generating description with GPT-4"
- **Errors**: "No images found for search query"
- **Form Validation**: "Required field is empty"

### Verbosity Levels

1. **Quiet**: Essential information only
2. **Normal**: Standard announcements (default)
3. **Verbose**: Detailed descriptions and context

### Live Regions

Dynamic content updates are announced automatically:
- Search results loading
- Image descriptions generated
- Vocabulary words added
- Status messages

### Screen Reader Integration

#### Windows (NVDA/JAWS)
```python
# Automatic detection
screen_reader = ScreenReaderSupport()
if screen_reader.screen_reader_detected:
    # Use screen reader announcements
    screen_reader.announce("Welcome to Unsplash Image Search")
else:
    # Use built-in TTS
    screen_reader.announce("Welcome", priority="assertive")
```

#### macOS (VoiceOver)
```python
# VoiceOver integration
screen_reader.announce("Image loaded", priority="polite")
```

#### Linux (Orca)
```python
# AT-SPI integration
screen_reader.announce("Search completed", priority="assertive")
```

## Visual Accessibility

### High Contrast Themes

Four high contrast options are available:

1. **High Contrast Dark** (Default)
   - Background: Pure black (#000000)
   - Text: Pure white (#FFFFFF)
   - Highlights: Bright yellow (#FFFF00)

2. **High Contrast Light**
   - Background: Pure white (#FFFFFF) 
   - Text: Pure black (#000000)
   - Highlights: Bright blue (#0000FF)

3. **Yellow on Black**
   - Background: Black (#000000)
   - Text: Bright yellow (#FFFF00)
   - Highlights: White (#FFFFFF)

4. **White on Black**
   - Background: Black (#000000)
   - Text: White (#FFFFFF)
   - Highlights: Bright blue (#0080FF)

All themes meet WCAG 2.1 AA contrast requirements (4.5:1 minimum ratio).

### Color Blind Accessibility

Three specialized color schemes:

1. **Deuteranopia Mode** (Green-blind)
   - Uses blue and orange instead of green/red
   - Pattern symbols supplement colors
   - High contrast combinations

2. **Protanopia Mode** (Red-blind)  
   - Blue and orange primary colors
   - Brown instead of red for errors
   - Enhanced brightness differences

3. **Tritanopia Mode** (Blue-blind)
   - Pink-red and green combinations
   - Purple for information
   - Avoiding blue-yellow confusion

### Font Scaling

- **Range**: 50% to 200% in 10% increments
- **Applies to**: All text including buttons, labels, and content
- **Preserves**: Layout proportions and readability
- **Shortcuts**: `Ctrl+Plus/Minus` for quick adjustment

### Focus Indicators

Enhanced visual focus indicators:
- **Width**: 3px border (customizable 1-5px)
- **Color**: High contrast color (customizable)
- **Style**: Solid border with offset
- **Fallback**: For widgets that don't support highlighting

## Audio Feedback

### Sound Types

| Sound | When Played | Description |
|-------|-------------|-------------|
| Success | Actions complete successfully | Pleasant chord |
| Error | Errors or failures occur | Low warning tone |
| Warning | Warnings or cautions | High alert tone |
| Info | Information messages | Single tone |
| Click | Button presses | Short click sound |
| Focus | Element focus changes | Subtle navigation tone |
| Notification | New messages/alerts | Ascending tones |

### Audio Configuration

```python
# Enable sound cues
accessibility.toggle_sound_cues()

# Adjust volume
accessibility.sound_manager.set_volume(0.7)  # 70%

# Test sounds
accessibility.sound_manager.test_sounds()
```

### Platform Audio Support

- **Windows**: SAPI (built-in), pygame, pydub
- **macOS**: System 'say' command, pygame, pydub  
- **Linux**: espeak, festival, spd-say, pygame

## Development Guide

### Making Widgets Accessible

```python
from src.ui.accessibility import AccessibilityManager

# Initialize
accessibility = AccessibilityManager(root)

# Basic accessibility
accessible_widget = accessibility.make_accessible(
    widget,
    name="Descriptive name",
    description="Additional context", 
    role="button"  # or "textbox", "list", etc.
)

# Advanced options
accessibility.make_accessible(
    widget,
    name="Search Button",
    description="Searches for images on Unsplash using your query",
    role="button",
    tab_index=1,  # Custom tab order
    focusable=True,
    skip_tab=False
)
```

### Custom Shortcuts

```python
# Add widget-specific shortcuts
keyboard_nav.add_widget(
    widget,
    shortcut_keys={
        '<Control-s>': save_function,
        '<F5>': refresh_function
    },
    context='forms'
)

# Customize global shortcuts
keyboard_nav.customize_shortcut(
    'toggle_high_contrast',
    '<Control-Shift-h>'
)
```

### Screen Reader Integration

```python
# Basic announcements
accessibility.announce("Action completed", priority="polite")
accessibility.announce("Error occurred", priority="assertive")

# Widget-specific announcements
def on_button_click():
    accessibility.announce("Searching for images")
    # ... perform action
    accessibility.announce("Search completed. 10 images found")
```

### Theme Integration

```python
# Apply accessibility themes
theme_manager = AccessibilityThemeManager()

# High contrast
theme_manager.set_high_contrast_mode('high_contrast_dark')
colors = theme_manager.get_current_colors()

# Color blind mode
theme_manager.set_color_blind_mode('deuteranopia')
cb_colors = theme_manager.get_current_colors()

# Test color accessibility
test_result = theme_manager.test_color_accessibility('#000000', '#FFFFFF')
print(f"Contrast ratio: {test_result['contrast_ratio']}")
print(f"WCAG AA compliant: {test_result['wcag_aa_compliant']}")
```

### Focus Management

```python
# Add widgets to focus management
focus_manager.add_widget(
    widget,
    tab_index=5,
    focusable=True,
    focus_ring=True,
    aria_label="Image search input"
)

# Custom tab order
focus_manager.set_tab_order([widget1, widget2, widget3])

# Navigation methods
focus_manager.focus_first()
focus_manager.focus_next()
focus_manager.focus_previous()
```

## Testing

### Automated Accessibility Testing

```python
# Run accessibility diagnostics
accessibility.run_accessibility_check()

# Check contrast ratios
theme_manager = AccessibilityThemeManager()
results = theme_manager.test_color_accessibility('#000000', '#FFFFFF')

# Validate tab order
focus_manager = accessibility.focus_manager
issues = focus_manager.validate_tab_order()
```

### Manual Testing Procedures

#### Keyboard Navigation Test
1. Unplug mouse or use keyboard-only mode
2. Navigate entire application using only keyboard
3. Ensure all functionality is accessible via keyboard
4. Test custom shortcuts and key combinations

#### Screen Reader Test  
1. Enable NVDA, JAWS, or system screen reader
2. Navigate application with screen reader active
3. Verify announcements are clear and helpful
4. Test form filling and button activation

#### High Contrast Test
1. Enable high contrast mode
2. Verify all text is readable
3. Check that focus indicators are visible
4. Ensure no information is conveyed by color alone

#### Color Blind Test
1. Enable color blind modes
2. Verify interface remains usable
3. Check that status indicators use symbols/patterns
4. Test with color blind simulation tools

### Testing Checklist

- [ ] All widgets are keyboard accessible
- [ ] Tab order is logical
- [ ] Focus indicators are visible
- [ ] Screen reader announcements are appropriate
- [ ] High contrast mode works correctly
- [ ] Color blind modes are functional
- [ ] Font scaling works at all levels
- [ ] Sound cues play correctly (when enabled)
- [ ] Shortcuts work as expected
- [ ] Help system is accessible
- [ ] Error messages are announced
- [ ] Form validation provides audio feedback

## Troubleshooting

### Common Issues

#### Screen Reader Not Working
**Symptoms**: No text-to-speech, announcements not heard
**Solutions**:
1. Check if screen reader is enabled in settings
2. Verify system screen reader (NVDA/JAWS) is running
3. Test built-in TTS with `Ctrl+Alt+R`
4. Check audio volume and output device

#### Keyboard Navigation Problems
**Symptoms**: Tab key doesn't work, widgets not focusable
**Solutions**:
1. Enable keyboard navigation in settings
2. Check tab order with `Ctrl+Alt+S` → Navigation tab
3. Verify widgets have proper `takefocus` setting
4. Reset to default navigation order

#### High Contrast Not Applying
**Symptoms**: Colors don't change, contrast insufficient
**Solutions**:
1. Try different high contrast themes
2. Check if custom theme is interfering
3. Restart application after changing theme
4. Verify theme files are not corrupted

#### Sound Cues Not Playing
**Symptoms**: No audio feedback, silent operation
**Solutions**:
1. Enable sound cues in settings
2. Check system volume and audio device
3. Test different audio backends
4. Verify audio permissions (macOS/Linux)

#### Font Scaling Issues
**Symptoms**: Text too small/large, layout broken
**Solutions**:
1. Reset font scale to 100% with `Ctrl+0`
2. Use preset font sizes (50%, 75%, 100%, etc.)
3. Check that application fonts support scaling
4. Restart application if layout is corrupted

### Debug Mode

Enable debug mode for troubleshooting:

```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Test accessibility features
accessibility.run_accessibility_check()

# Debug widget info
# Press Ctrl+Alt+D while focused on any widget
```

### Platform-Specific Issues

#### Windows
- **NVDA Integration**: Ensure NVDA is running and UI Automation is enabled
- **High DPI**: Font scaling may need adjustment on high-DPI displays
- **Permissions**: Some audio backends may require administrator privileges

#### macOS  
- **VoiceOver**: Enable in System Preferences → Accessibility
- **Audio**: Grant microphone permissions if TTS fails
- **Keyboard**: Enable full keyboard access in System Preferences

#### Linux
- **AT-SPI**: Install and configure AT-SPI for screen reader support
- **Audio**: Install pulseaudio and ALSA for sound cues
- **Permissions**: Ensure user has access to audio devices

### Getting Help

1. **In-Application Help**: Press `F1` or `Ctrl+Alt+A`
2. **Settings Diagnostics**: `Ctrl+Alt+S` → Advanced → Run Accessibility Check
3. **Documentation**: Refer to this guide and inline help text
4. **Debug Output**: Enable logging to see detailed error messages

## Standards Compliance

### WCAG 2.1 Guidelines

| Guideline | Level | Status |
|-----------|-------|--------|
| Keyboard Accessible | AA | ✅ Compliant |
| No Keyboard Trap | A | ✅ Compliant |
| Timing Adjustable | A | ✅ Compliant |
| Pause, Stop, Hide | A | ✅ Compliant |
| No Seizures | A | ✅ Compliant |
| Bypass Blocks | AA | ✅ Compliant |
| Page Titles | A | ✅ Compliant |
| Focus Order | A | ✅ Compliant |
| Link Purpose | AA | ✅ Compliant |
| Multiple Ways | AA | ✅ Compliant |
| Headings and Labels | AA | ✅ Compliant |
| Focus Visible | AA | ✅ Compliant |
| Contrast Minimum | AA | ✅ Compliant |
| Resize Text | AA | ✅ Compliant |
| Images of Text | AA | ✅ Compliant |
| Reflow | AA | ✅ Compliant |

### Section 508 Compliance

The application meets Section 508 requirements for:
- Keyboard accessibility
- Screen reader compatibility  
- Color and contrast
- Timed events
- Alternative formats

### Platform Guidelines

- **Windows**: Follows Microsoft Accessibility Guidelines
- **macOS**: Conforms to Apple Accessibility Guidelines
- **Linux**: Implements GNOME Accessibility Standards

## Conclusion

The accessibility implementation provides comprehensive support for users with disabilities while maintaining excellent usability for all users. The modular design allows for easy customization and extension of accessibility features.

For additional help or feature requests, please refer to the application's help system or contact support.

---

**Last Updated**: 2024
**Version**: 1.0
**Compliance**: WCAG 2.1 AA, Section 508