# ClickableText Component

A sophisticated text widget that makes Spanish words clickable for vocabulary learning, with automatic translation and CSV storage integration.

## Overview

The `ClickableText` component extends `tkinter.scrolledtext.ScrolledText` to provide:

- **Word-level clicking**: Individual Spanish words become clickable
- **Automatic translation**: Uses OpenAI API to translate clicked words
- **Vocabulary management**: Saves translations to CSV with context
- **Visual feedback**: Temporary highlighting and popup confirmations
- **Theme integration**: Works with existing theme system
- **Smart filtering**: Skips common words and duplicates

## Features

### 🎯 Core Functionality
- **Click Detection**: Precise word boundary detection using text indices
- **Spanish Word Recognition**: Identifies Spanish words using character patterns and length heuristics
- **Real-time Translation**: Automatic translation via OpenAI API with error handling
- **Context Extraction**: Captures surrounding words for better vocabulary context
- **Duplicate Prevention**: Checks existing vocabulary to avoid redundancy

### 🎨 User Experience
- **Visual Highlighting**: Temporary yellow highlight when words are clicked
- **Popup Confirmations**: Success/error popups with auto-close timers
- **Cursor Changes**: Hand cursor on hover over clickable words
- **Theme Consistency**: Inherits colors and styling from theme manager
- **Non-blocking Operations**: Translation runs in background threads

### 📊 Data Management
- **CSV Integration**: Automatic saving to vocabulary CSV files
- **Structured Storage**: Spanish, English, Date, Search Query, Image URL, Context
- **Cache Management**: In-memory vocabulary cache for fast duplicate checking
- **Context Preservation**: Stores surrounding text for learning context

## Implementation

### File Structure
```
src/ui/components/clickable_text.py    # Main component
src/examples/clickable_text_integration.py  # Integration guide
tests/test_clickable_text.py          # Test suite
demo_clickable_text.py                # Standalone demo
docs/CLICKABLE_TEXT_COMPONENT.md      # This documentation
```

### Core Classes

#### `ClickableText`
Main component extending `scrolledtext.ScrolledText`:
```python
class ClickableText(scrolledtext.ScrolledText):
    def __init__(self, parent, vocabulary_manager, openai_service, 
                 theme_manager, current_search_query="", current_image_url="", **kwargs)
```

**Key Methods:**
- `_make_text_clickable()`: Processes text to make Spanish words clickable
- `_is_likely_spanish_word()`: Filters words using smart heuristics
- `_on_word_click()`: Handles word click events
- `_translate_and_add_word()`: Background translation and vocabulary addition
- `set_clickable()`: Enable/disable clicking functionality
- `update_context()`: Update search query and image URL context

#### Word Detection Algorithm
```python
# Spanish word pattern with accent support
word_pattern = r'\b[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+\b'

# Smart filtering logic
def _is_likely_spanish_word(self, word: str) -> bool:
    # Skip common articles, prepositions, conjunctions
    # Skip if already in vocabulary
    # Prioritize words with Spanish characters
    # Include reasonable length words (≥4 chars)
```

### Integration with Existing System

#### Theme Manager Integration
```python
# Automatic theme callback registration
self.theme_manager.register_theme_callback(self._on_theme_changed)

# Dynamic color application
colors = self.theme_manager.get_colors()
self.tag_configure("highlight", 
                  background=colors.get('select_bg'),
                  foreground=colors.get('select_fg'))
```

#### Vocabulary Manager Integration
```python
# Automatic vocabulary entry creation
vocab_entry = VocabularyEntry(
    spanish=word,
    english=translation,
    search_query=self.current_search_query,
    image_url=self.current_image_url,
    context=context
)
success = self.vocabulary_manager.add_vocabulary_entry(vocab_entry)
```

#### OpenAI Service Integration
```python
# Translation with error handling
def _translate_word(self, word: str) -> str:
    prompt = f"Translate this Spanish word to English: '{word}'"
    response = self.openai_service.client.chat.completions.create(
        model=self.openai_service.model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.0
    )
    return response.choices[0].message.content.strip()
```

## Usage

### Basic Integration
Replace existing `scrolledtext.ScrolledText` with `ClickableText`:

```python
# OLD CODE:
self.description_text = scrolledtext.ScrolledText(
    desc_frame, wrap=tk.WORD, state=tk.DISABLED, font=("TkDefaultFont", 12)
)

# NEW CODE:
from src.ui.components.clickable_text import ClickableText

self.description_text = ClickableText(
    desc_frame,
    vocabulary_manager=self.vocabulary_manager,
    openai_service=self.openai_service,
    theme_manager=self.theme_manager,
    wrap=tk.WORD,
    state=tk.DISABLED,
    font=("TkDefaultFont", 12)
)
```

### Context Updates
```python
def display_description(self, text):
    self.description_text.config(state=tk.NORMAL)
    self.description_text.clear()
    
    # Update context for new vocabulary entries
    self.description_text.update_context(
        search_query=self.current_query,
        image_url=self.current_image_url
    )
    
    self.description_text.insert(tk.END, text)
    self.description_text.config(state=tk.DISABLED)
```

### Runtime Control
```python
# Enable/disable clicking
self.description_text.set_clickable(True)

# Register callbacks for events
self.description_text.register_click_callback('word_added', callback)

# Check if word would be clickable
if self.description_text._is_likely_spanish_word("hermosa"):
    print("Word would be clickable")
```

## Technical Details

### Text Processing
- **Index Calculation**: Converts character positions to tkinter text indices
- **Boundary Detection**: Finds word boundaries using character analysis
- **Tag Management**: Uses tkinter text tags for clickable regions and highlighting
- **Event Binding**: Binds mouse events to specific text regions

### Threading Model
- **UI Thread**: Handles clicks, highlighting, and popup display
- **Background Threads**: Performs API calls for translation
- **Thread Safety**: Uses `after()` method for UI updates from background threads

### Error Handling
- **API Failures**: Graceful degradation with error popups
- **Translation Errors**: Fallback to "[Translation failed]" text
- **File I/O Errors**: Continues operation even if CSV writing fails
- **Widget Cleanup**: Proper popup window destruction on widget destroy

### Performance Optimizations
- **Vocabulary Caching**: In-memory set for O(1) duplicate checking
- **Lazy Processing**: Text processing only on modification
- **Event Debouncing**: Prevents excessive tag recalculation
- **Background Processing**: Non-blocking translation operations

## Configuration

### Word Filtering
Customize which words are clickable by modifying `_is_likely_spanish_word()`:

```python
# Add custom skip words
skip_words = {
    'el', 'la', 'de', 'en', 'con', 'que', 'como',
    # Add your own common words to skip
}

# Adjust minimum word length
if len(word) >= 3:  # Change from 4 to 3 for shorter words
    return True
```

### Theme Customization
The component automatically inherits theme colors but can be customized:

```python
# Custom highlight colors
colors = self._get_theme_colors()
colors['word_highlight'] = '#ffff00'  # Custom yellow
colors['success_color'] = '#00ff00'   # Custom green
```

### Translation Behavior
Modify translation prompts for different behavior:

```python
# More detailed translations
prompt = f"Translate '{word}' to English and provide the most common meaning with brief context"

# Regional variations
prompt = f"Translate this Latin American Spanish word to English: '{word}'"
```

## Testing

### Unit Tests
```bash
# Run unit tests
python tests/test_clickable_text.py --unit

# Run visual test
python tests/test_clickable_text.py --visual
```

### Demo Application
```bash
# Run standalone demo
python demo_clickable_text.py
```

### Integration Testing
```bash
# Test with existing application
python src/examples/clickable_text_integration.py
```

## File Outputs

### Vocabulary CSV Format
```csv
Spanish,English,Date,Search Query,Image URL,Context
playa,beach,2025-01-15 14:30,tropical paradise,https://images.unsplash.com/123,una playa hermosa con agua cristalina
hermosa,beautiful,2025-01-15 14:32,tropical paradise,https://images.unsplash.com/123,Esta imagen muestra una playa hermosa
```

### Demo Vocabulary
The demo creates `demo_vocabulary.csv` with sample translations to show functionality without requiring API setup.

## Compatibility

### Requirements
- Python 3.7+
- tkinter (included with Python)
- OpenAI Python client (for translation)
- pathlib (included with Python 3.4+)

### Optional Dependencies
- Theme manager (graceful degradation if not available)
- Vocabulary manager (basic functionality without persistence)
- OpenAI service (shows click events without translation)

### Backward Compatibility
- Drop-in replacement for `scrolledtext.ScrolledText`
- All existing ScrolledText methods work unchanged
- Additional functionality is additive, not breaking

## Troubleshooting

### Common Issues

**"No module named 'ui'" Error:**
```python
# Add to sys.path before importing
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))
```

**Words Not Clickable:**
- Check `is_clickable` property is True
- Verify words pass `_is_likely_spanish_word()` filter
- Ensure text has been processed with `_make_text_clickable()`

**Translation Failures:**
- Verify OpenAI API key configuration
- Check internet connection
- Monitor console for API error messages

**Theme Not Applied:**
- Ensure theme manager is initialized before component
- Check theme callback registration
- Verify theme manager has valid colors

**CSV Not Saving:**
- Check file permissions in data directory
- Verify VocabularyManager initialization
- Check CSV file path exists

### Debug Mode
Enable debug output:

```python
# Add debug prints to see word processing
def _is_likely_spanish_word(self, word):
    result = # ... existing logic
    print(f"Word '{word}': clickable={result}")
    return result
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: Support for other languages besides Spanish
- **Custom Translation Services**: Support for Google Translate, DeepL, etc.
- **Pronunciation Integration**: Audio pronunciation of clicked words
- **Difficulty Levels**: Filter words by difficulty/frequency
- **Progress Tracking**: Track learning progress and word retention

### Performance Improvements
- **Caching Translations**: Cache common word translations
- **Batch Processing**: Batch multiple translation requests
- **Offline Mode**: Basic functionality without internet
- **Smart Prefetching**: Pre-translate visible words

### UI Enhancements
- **Better Popups**: More sophisticated popup design
- **Inline Definitions**: Show definitions inline instead of popups
- **Word Hints**: Preview translation on hover
- **Progress Indicators**: Show vocabulary learning progress

## Contributing

When modifying the ClickableText component:

1. **Maintain Compatibility**: Ensure backward compatibility with ScrolledText
2. **Test Thoroughly**: Run both unit tests and visual tests
3. **Update Documentation**: Keep this document current
4. **Follow Patterns**: Use existing code patterns for consistency
5. **Error Handling**: Add appropriate try/catch blocks for new features

## License

This component is part of the Unsplash Image Search & GPT Description application and follows the same license terms.