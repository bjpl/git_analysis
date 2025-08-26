# Description Style Selector System

## Overview

The Description Style Selector system provides users with three distinct styles for generating AI-powered Spanish descriptions:

1. **Academic/Neutral** - Formal, objective, educational tone
2. **Poetic/Literary** - Expressive, metaphorical, artistic language  
3. **Technical/Scientific** - Precise, detailed, terminology-focused

## Key Features

### ✅ Implemented Components

#### 1. Core Style System (`src/features/description_styles.py`)
- **DescriptionStyleManager**: Main coordinator class
- **BaseDescriptionStyleHandler**: Abstract base for style handlers
- **AcademicNeutralStyleHandler**: Academic/formal style implementation
- **PoeticLiteraryStyleHandler**: Creative/artistic style implementation  
- **TechnicalScientificStyleHandler**: Technical/scientific style implementation
- **Style and VocabularyLevel enums**: Type-safe style definitions

#### 2. UI Components (`src/ui/components/style_selector.py`)
- **StyleSelectorPanel**: Embeddable UI widget for style selection
- **StyleSelectorDialog**: Standalone dialog for style configuration
- Radio button interface for style selection
- Dropdown for vocabulary level selection (Beginner → Native)
- Live preview of style characteristics
- Reset to defaults functionality

#### 3. Session Integration (`src/features/session_tracker.py`)
- **Enhanced SessionStats**: Now includes style preferences
- **Persistent storage**: Style preferences saved to JSON
- **Usage analytics**: Track style usage patterns over time
- **Backwards compatibility**: Graceful handling of legacy data

#### 4. Main Application Integration (`main.py`)
- **Dynamic prompt generation**: Uses selected style for GPT prompts
- **Context-aware vocabulary extraction**: Style-specific vocabulary parsing
- **Live style switching**: Immediate effect on description generation
- **Preference persistence**: Settings survive app restarts

#### 5. Comprehensive Testing (`tests/test_description_styles.py`)
- Unit tests for all style handlers
- UI component testing with Tkinter
- Session persistence testing
- Integration testing with main application
- Error handling and fallback scenarios

## Style Characteristics

### Academic/Neutral Style
```python
# Characteristics
- Formal, objective tone
- Educational vocabulary  
- Structured descriptions
- Academic connectors (sin embargo, por lo tanto)
- Systematic detail presentation

# Example phrases
"Se observa una composición equilibrada"
"Los elementos predominantes incluyen"
"En términos de iluminación, se aprecia"
```

### Poetic/Literary Style
```python
# Characteristics  
- Creative, expressive language
- Metaphors and sensory descriptions
- Artistic vocabulary
- Emotional atmosphere
- Varied sentence rhythm

# Example phrases
"Los colores danzan en armonía"
"La luz acaricia suavemente"
"Como si fuera un lienzo viviente"
```

### Technical/Scientific Style
```python
# Characteristics
- Precise, specialized terminology
- Quantitative descriptions
- Systematic analysis
- Technical specifications
- Professional language

# Example phrases
"Las propiedades ópticas evidencian"
"La estructura compositiva presenta"
"El análisis cuantitativo revela"
```

## Vocabulary Levels

Each style adapts to four vocabulary complexity levels:

- **Beginner**: Basic vocabulary, simple structures
- **Intermediate**: Varied vocabulary, common expressions
- **Advanced**: Sophisticated vocabulary, complex structures  
- **Native**: Complete vocabulary with idioms and colloquialisms

## Usage Examples

### Basic Usage
```python
from src.features.description_styles import get_style_manager, DescriptionStyle, VocabularyLevel

# Get the global style manager
style_manager = get_style_manager()

# Set style and level
style_manager.set_current_style(DescriptionStyle.POETIC)
style_manager.set_vocabulary_level(VocabularyLevel.ADVANCED)

# Generate style-specific prompt
prompt = style_manager.generate_description_prompt(
    context="Una fotografía de paisaje montañoso",
    focus_areas=["colores del atardecer", "texturas rocosas"]
)

# Generate vocabulary extraction prompt
vocab_prompt = style_manager.get_vocabulary_extraction_prompt(description_text)
```

### UI Integration
```python
from src.ui.components.style_selector import StyleSelectorPanel

def on_style_change(style, vocabulary_level):
    print(f"Style changed to: {style.value}, Level: {vocabulary_level.value}")

# Create embeddable panel
style_panel = StyleSelectorPanel(
    parent_widget,
    session_tracker=session_tracker,
    style_change_callback=on_style_change
)
```

### Session Persistence
```python
from src.features.session_tracker import SessionTracker

tracker = SessionTracker(data_directory)

# Save style preferences
preferences = {
    'description_style': 'technical',
    'vocabulary_level': 'advanced'
}
tracker.save_style_preferences(preferences)

# Load preferences
loaded_prefs = tracker.load_style_preferences()

# Get usage statistics
stats = tracker.get_style_usage_stats()
```

## File Structure

```
src/
├── features/
│   ├── description_styles.py      # Core style system
│   └── session_tracker.py         # Enhanced with style persistence
├── ui/
│   └── components/
│       └── style_selector.py      # UI components
tests/
└── test_description_styles.py     # Comprehensive test suite
docs/
└── STYLE_SELECTOR_SYSTEM.md      # This documentation
```

## Integration Points

### Main Application (main.py)
1. **Initialization**: Style manager and session tracker setup
2. **UI Integration**: Style selector panel embedded in main interface  
3. **Prompt Generation**: Dynamic prompt creation based on selected style
4. **Vocabulary Extraction**: Style-aware vocabulary parsing
5. **Preference Management**: Load/save style preferences

### Configuration Management
- Style preferences stored separately from API configuration
- JSON format for easy reading/writing
- Graceful fallbacks for missing or corrupted preference files

### Error Handling
- Robust fallbacks when style system is unavailable
- Graceful degradation if dependencies are missing
- User-friendly error messages in UI components

## Performance Considerations

1. **Lazy Loading**: Style handlers initialized only when needed
2. **Caching**: Style preferences cached during session
3. **Efficient Storage**: Minimal JSON footprint for preferences
4. **Background Processing**: Style changes don't block UI

## Future Enhancements

### Potential Additions
1. **Custom Styles**: User-defined style templates
2. **Style Templates**: Pre-configured style combinations
3. **Export/Import**: Share style configurations between users
4. **Analytics Dashboard**: Detailed style usage visualizations
5. **A/B Testing**: Compare effectiveness of different styles
6. **Context Detection**: Automatic style suggestions based on image content

### Accessibility Improvements
1. **Keyboard Navigation**: Full keyboard support for style selection
2. **Screen Reader Support**: ARIA labels and descriptions
3. **High Contrast**: Style selector works with accessibility themes
4. **Font Scaling**: Respect system font size preferences

## Testing

Run the comprehensive test suite:
```bash
cd unsplash-image-search-gpt-description
python -m pytest tests/test_description_styles.py -v
```

Test coverage includes:
- ✅ Core style system functionality
- ✅ Individual style handler behavior  
- ✅ UI component creation and interaction
- ✅ Session persistence and loading
- ✅ Integration with main application
- ✅ Error handling and edge cases

## Conclusion

The Description Style Selector system provides a robust, extensible framework for customizing AI-generated Spanish descriptions. With three distinct styles, four vocabulary levels, persistent preferences, and comprehensive UI integration, users can tailor their learning experience to their specific needs and preferences.

The system is designed for maintainability, testability, and future expansion while providing immediate value through improved vocabulary learning and description quality.