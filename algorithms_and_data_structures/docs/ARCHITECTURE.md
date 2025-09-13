# Architecture Documentation

## Overview

The Algorithms & Data Structures Learning Platform has been refactored to follow clean architecture principles with proper separation of concerns and state management.

## Directory Structure

```
algorithms_and_data_structures/
├── src/
│   ├── core/                    # Core business logic
│   │   ├── curriculum.py       # Curriculum data management
│   │   └── progress.py         # Progress tracking
│   ├── ui/                     # UI components
│   │   ├── windows_formatter.py # Terminal formatting
│   │   ├── lesson_viewer.py    # Lesson display logic
│   │   └── enhanced_lesson_formatter.py # Enhanced formatting
│   ├── cli.py                  # Unified CLI entry point
│   ├── notes_manager.py        # Notes management
│   └── notes_viewer.py         # Notes display
├── data/                        # Data files
│   └── curriculum.json         # Curriculum content
├── main.py                     # Application entry point
└── progress.json               # User progress tracking
```

## Key Components

### 1. Core Layer (`src/core/`)

**Purpose**: Contains all business logic, data models, and domain rules.

- **curriculum.py**: Manages curriculum data
  - `Lesson`: Data model for lessons
  - `Module`: Data model for modules
  - `CurriculumManager`: Handles curriculum operations

- **progress.py**: Manages user progress
  - `UserProgress`: Progress data model
  - `ProgressManager`: Progress persistence and operations

### 2. UI Layer (`src/ui/`)

**Purpose**: Handles all user interface and display logic.

- **lesson_viewer.py**: Dedicated lesson display
  - No recursive menu loops
  - Clean separation from navigation

- **windows_formatter.py**: Terminal formatting
  - Consistent styling across the application
  - Windows-compatible output

### 3. Unified CLI (`src/cli.py`)

**Purpose**: Main application controller with proper state management.

#### State Management

Uses an enum-based state machine to prevent recursion:

```python
class MenuState(Enum):
    MAIN_MENU = "main_menu"
    BROWSE_MODULES = "browse_modules"
    BROWSE_LESSONS = "browse_lessons"
    VIEW_LESSON = "view_lesson"
    # ...
```

#### Key Features

1. **No Recursion**: Each menu action changes state instead of calling itself
2. **Clear Navigation**: State machine makes navigation flow explicit
3. **Error Handling**: Graceful error recovery with state reset
4. **Data Consistency**: Centralized data access through managers

## Data Flow

```
User Input → CLI State Machine → Core Managers → UI Components → Display
                ↑                                              ↓
                └──────────── State Change ←──────────────────┘
```

## Key Improvements

### 1. Fixed Recursive Menu Issues

**Before**: Menu functions called themselves recursively
```python
def show_menu():
    choice = input()
    if choice == "1":
        show_submenu()
        show_menu()  # Recursive call
```

**After**: State-based navigation
```python
def handle_menu():
    choice = input()
    if choice == "1":
        self.state = MenuState.SUBMENU  # State change
```

### 2. Standardized Data Models

**Before**: Inconsistent dictionary structures
```python
lesson = {"title": "...", "content": {...}}  # Nested, inconsistent
```

**After**: Dataclass models with validation
```python
@dataclass
class Lesson:
    id: str
    title: str
    content: str
    # ... typed fields
```

### 3. Separation of Concerns

**Before**: Mixed UI and business logic
```python
def start_lesson(lesson):
    # Display logic
    print(lesson)
    # Business logic
    progress["completed"].append(lesson["id"])
    # More display
    show_menu()
```

**After**: Clear separation
```python
# UI Layer
def display_lesson(lesson):
    # Only display logic
    
# Core Layer
def mark_complete(lesson_id):
    # Only business logic
```

## Testing Strategy

1. **Unit Tests**: Test core logic independently
2. **Integration Tests**: Test component interactions
3. **UI Tests**: Test display and navigation flow

## Future Enhancements

1. **Plugin System**: Add new lesson types dynamically
2. **Cloud Sync**: Sync progress across devices
3. **AI Integration**: Enhanced Claude AI features
4. **Analytics**: Learning analytics and insights

## Migration Guide

For users of the old system:

1. **Progress**: Automatically migrated from `progress.json`
2. **Notes**: Compatible with existing notes database
3. **Commands**: Run with `python main.py` or `python src/cli.py`

## Benefits

1. **Maintainability**: Clean separation makes changes easier
2. **Testability**: Each component can be tested independently
3. **Scalability**: Easy to add new features without breaking existing ones
4. **Reliability**: No recursion issues or stack overflows
5. **User Experience**: Smoother navigation and consistent display
