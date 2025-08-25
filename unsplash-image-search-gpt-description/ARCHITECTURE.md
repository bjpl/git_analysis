# Modular Architecture Documentation

## Overview

The Unsplash Image Search application has been refactored from a monolithic `main.py` file into a clean, modular architecture that follows separation of concerns principles.

## Directory Structure

```
src/
├── __init__.py                 # Package initialization
├── app.py                      # Main application entry point
├── ui/                         # User Interface Layer
│   ├── __init__.py
│   ├── main_window.py         # Main GUI window class
│   ├── widgets/               # Reusable UI components
│   │   ├── __init__.py
│   │   ├── image_viewer.py    # Image display widget
│   │   ├── vocabulary_list.py # Vocabulary list widget
│   │   └── search_bar.py      # Search input widget
│   └── dialogs/               # Dialog windows
│       ├── __init__.py
│       └── setup_wizard.py    # API key setup dialog
├── services/                  # Business Logic Layer
│   ├── __init__.py
│   ├── unsplash_service.py    # Unsplash API client
│   ├── openai_service.py      # OpenAI GPT client
│   └── translation_service.py # Translation logic
├── models/                    # Data Models Layer
│   ├── __init__.py
│   ├── session.py             # Session data model
│   ├── vocabulary.py          # Vocabulary management
│   └── image.py              # Image data model
└── utils/                     # Utility Layer
    ├── __init__.py
    ├── cache.py              # LRU cache for images
    ├── data_export.py        # Export functionality
    └── file_manager.py       # File operations
```

## Architecture Layers

### 1. UI Layer (`src/ui/`)

**Purpose**: Handles all user interface components and user interactions.

- **main_window.py**: Main application window that coordinates all UI components
- **widgets/**: Reusable UI components (image viewer, search bar, vocabulary lists)
- **dialogs/**: Modal dialogs (setup wizard, export dialogs)

**Key Features**:
- Clean separation between UI and business logic
- Reusable widget components
- Event-driven architecture with callbacks

### 2. Services Layer (`src/services/`)

**Purpose**: Encapsulates external API interactions and core business logic.

- **unsplash_service.py**: Handles all Unsplash API operations
- **openai_service.py**: Manages OpenAI GPT API calls
- **translation_service.py**: Coordinates translation workflows

**Key Features**:
- API abstraction with error handling
- Retry logic with exponential backoff
- Service composition (translation service uses OpenAI service)

### 3. Models Layer (`src/models/`)

**Purpose**: Defines data structures and manages application state.

- **session.py**: Session tracking and logging
- **vocabulary.py**: Vocabulary management and CSV operations
- **image.py**: Image search state and pagination

**Key Features**:
- Clean data models with serialization support
- State management patterns
- Data validation and type safety

### 4. Utils Layer (`src/utils/`)

**Purpose**: Provides common utilities and helper functions.

- **cache.py**: LRU cache implementation for images and search results
- **data_export.py**: Export functionality for different formats
- **file_manager.py**: File operations and path management

**Key Features**:
- Reusable utility classes
- Performance optimization (caching)
- Cross-platform file operations

## Key Design Patterns

### 1. Separation of Concerns
Each layer has a distinct responsibility:
- UI handles presentation
- Services handle business logic
- Models handle data
- Utils handle common operations

### 2. Dependency Injection
Services and managers are injected into the main window, making testing easier and reducing coupling.

### 3. Observer Pattern
UI components use callbacks to communicate with the main window, avoiding tight coupling.

### 4. Strategy Pattern
Different export formats are handled through configurable strategies.

### 5. Factory Pattern
Data models can be created from dictionaries or CSV rows using class methods.

## Migration from Monolithic Architecture

### Before (main.py - ~1000+ lines)
- Single large class with all functionality
- Mixed UI and business logic
- Difficult to test individual components
- Hard to maintain and extend

### After (Modular Architecture)
- Clean separation into logical modules
- Each module < 500 lines
- Testable components
- Easy to extend and maintain

## Benefits of Modular Architecture

### 1. Maintainability
- Smaller, focused files are easier to understand
- Changes to one layer don't affect others
- Clear responsibility boundaries

### 2. Testability
- Each component can be unit tested in isolation
- Mock dependencies easily
- Better test coverage

### 3. Extensibility
- New features can be added without touching existing code
- Plugin-style architecture for widgets and services
- Easy to add new export formats or API services

### 4. Reusability
- UI widgets can be reused in other applications
- Services can be used independently
- Utility classes are application-agnostic

### 5. Team Development
- Multiple developers can work on different layers
- Reduced merge conflicts
- Clear interfaces between components

## Usage

### Running the Modular Version
```bash
python main_modular.py
```

### Running the Original Version (for comparison)
```bash
python main.py
```

### Importing Components
```python
# Import services
from src.services.unsplash_service import UnsplashService
from src.services.openai_service import OpenAIService

# Import models
from src.models.vocabulary import VocabularyManager
from src.models.session import SessionManager

# Import utilities
from src.utils.cache import ImageCache
```

## Testing Strategy

### Unit Testing
Each layer can be tested independently:

```python
# Test services
def test_unsplash_service():
    service = UnsplashService("test_key")
    # Test API interactions

# Test models
def test_vocabulary_manager():
    manager = VocabularyManager(Path("test.csv"))
    # Test data operations

# Test utilities
def test_image_cache():
    cache = ImageCache(max_size=5)
    # Test caching logic
```

### Integration Testing
Test interactions between layers:

```python
def test_translation_workflow():
    # Test complete translation workflow
    pass
```

## Performance Improvements

### 1. Caching
- LRU cache for images reduces network requests
- Search result caching improves response times

### 2. Threading
- API calls run in background threads
- UI remains responsive during operations

### 3. Memory Management
- Image cache has size limits
- Automatic cleanup of old entries

## Future Enhancements

### Planned Features
1. **Plugin System**: Allow custom export formats and API services
2. **Configuration Management**: Advanced settings and profiles
3. **Batch Operations**: Process multiple images at once
4. **Advanced Caching**: Persistent cache with expiration
5. **API Rate Limiting**: Intelligent request throttling

### Architecture Improvements
1. **Async/Await**: Convert to async operations for better performance
2. **Event System**: Implement publish/subscribe for loose coupling
3. **Database Integration**: Optional database backend for large vocabularies
4. **Microservices**: Split into separate processes for scalability

## Backwards Compatibility

The original `main.py` remains functional and unchanged. The modular version is available through `main_modular.py`, allowing for gradual migration and comparison.

## Migration Guide

To migrate existing customizations:

1. **UI Changes**: Move to appropriate widget files
2. **API Logic**: Move to service files
3. **Data Operations**: Move to model files
4. **Utilities**: Move to utils files

The main window class provides the same interface as the original, making migration straightforward.