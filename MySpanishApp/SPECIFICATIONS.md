# MySpanishApp - Technical Specifications

## 1. Overview

MySpanishApp is a PyQt6-based desktop application designed to help users track and manage their Spanish language learning journey through tutoring sessions. The application provides comprehensive tools for planning sessions, tracking vocabulary and grammar progress, and reviewing learning history.

### Purpose
- Track Spanish tutoring sessions with individual teachers
- Record vocabulary, grammar patterns, and learning challenges
- Review progress and learning patterns over time
- Export learning data for external use

### Technology Stack
- **Language**: Python 3.10+
- **GUI Framework**: PyQt6 (v6.8.1+)
- **Database**: SQLite3
- **Package Management**: Poetry
- **Testing**: pytest (v8.0.0+)

## 2. Architecture

### Application Structure
```
MySpanishApp/
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── models/              # Data models and database logic
│   ├── database.py      # SQLite connection manager
│   ├── session_model.py # Session CRUD operations
│   ├── vocab_model.py   # Vocabulary management
│   └── grammar_model.py # Grammar tracking
├── views/               # PyQt6 UI components
│   ├── main_window.py   # Main application window
│   ├── plan_view.py     # Session planning interface
│   ├── track_view.py    # Learning tracking interface
│   ├── review_view.py   # Progress review interface
│   ├── settings_view.py # Application settings
│   └── track_tabs/      # Sub-components for tracking
├── utils/               # Utility modules
│   ├── logger.py        # Logging configuration
│   └── export.py        # Data export functionality
└── tests/               # Test suite
```

### Design Patterns
- **MVC Pattern**: Clear separation between Models (data), Views (UI), and Controllers (business logic)
- **Singleton Pattern**: Database connection management
- **Observer Pattern**: UI updates based on data changes

## 3. Database Schema

### Tables

#### teachers
- `teacher_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `name` (TEXT, NOT NULL)
- `region` (TEXT)
- `notes` (TEXT)

#### sessions
- `session_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `teacher_id` (INTEGER, FOREIGN KEY → teachers)
- `session_date` (TEXT, format: YYYY-MM-DD)
- `start_time` (TEXT, format: HH:MM)
- `duration` (TEXT, e.g., "1h", "30m")
- `status` (TEXT: "planned", "completed", "cancelled")
- `timestamp` (TEXT, ISO format)

#### vocab
- `vocab_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `session_id` (INTEGER, FOREIGN KEY → sessions)
- `word_phrase` (TEXT, NOT NULL)
- `translation` (TEXT)
- `context_notes` (TEXT)
- `timestamp` (TEXT, ISO format)

#### vocab_regionalisms
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `vocab_id` (INTEGER, FOREIGN KEY → vocab)
- `country_name` (TEXT)

#### grammar
- `grammar_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `session_id` (INTEGER, FOREIGN KEY → sessions)
- `phrase_structure` (TEXT)
- `explanation` (TEXT)
- `resource_link` (TEXT)
- `timestamp` (TEXT, ISO format)

#### challenges
- `challenge_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `session_id` (INTEGER, FOREIGN KEY → sessions)
- `description` (TEXT)
- `type` (TEXT: "expression", "comprehension")
- `timestamp` (TEXT, ISO format)

#### comfort
- `comfort_id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `session_id` (INTEGER, FOREIGN KEY → sessions)
- `description` (TEXT)
- `timestamp` (TEXT, ISO format)

## 4. Core Features & User Flows

### 4.1 Plan Module

**Purpose**: Schedule and manage Spanish tutoring sessions

**User Flow**:
1. User navigates to Plan view (Ctrl+1 or click "📅 Plan")
2. Calendar widget displays current month
3. User clicks on a date to view/manage sessions
4. Sessions for selected date appear in the list
5. User can:
   - Add new session via "Add Session" button
   - Search existing sessions using search box
   - Right-click sessions to change status (planned/completed/cancelled)

**Components**:
- `PlanView` (views/plan_view.py:22): Main planning interface
- `SessionDialog` (views/session_dialog.py): Session creation/editing dialog
- `SessionModel` (models/session_model.py): Database operations

**Key Methods**:
- `load_sessions_for_date()` (plan_view.py:77): Fetches sessions for selected date
- `on_add_session_clicked()` (plan_view.py:106): Opens session creation dialog
- `change_session_status()` (plan_view.py:153): Updates session status

### 4.2 Track Module

**Purpose**: Record learning content during active sessions

**User Flow**:
1. User navigates to Track view (Ctrl+2 or click "📝 Track")
2. Selects active session from dropdown
3. Uses tabs to track different aspects:
   - **Vocabulary Tab**: Add words/phrases with translations
   - **Grammar Tab**: Record grammar patterns and explanations
   - **Challenges Tab**: Note expression/comprehension difficulties
   - **Comfort Tab**: Track areas of confidence
4. All entries are automatically linked to selected session

**Components**:
- `TrackView` (views/track_view.py:18): Main tracking interface
- `VocabTab` (views/track_tabs/vocab_tab.py): Vocabulary tracking
- `GrammarTab` (views/track_tabs/grammar_tab.py): Grammar tracking

**Key Methods**:
- `set_session_id()`: Updates current session for all tabs
- `add_vocab_item()`: Saves vocabulary to database
- `add_grammar_item()`: Saves grammar patterns

### 4.3 Review Module

**Purpose**: Analyze learning progress and patterns

**User Flow**:
1. User navigates to Review view (Ctrl+3 or click "📊 Review")
2. Dashboard displays:
   - Learning statistics (total sessions, vocabulary count)
   - Recent sessions list (filterable by status)
   - Recent vocabulary additions
3. User can refresh data using "Refresh Data" button
4. Filter sessions by status (All/Completed/Planned)

**Components**:
- `ReviewView` (views/review_view.py:14): Review dashboard
- Statistics aggregation from database

**Key Methods**:
- `refresh_stats()` (review_view.py:108): Updates statistics
- `refresh_sessions()` (review_view.py:134): Updates session list
- `refresh_vocab()` (review_view.py:159): Updates vocabulary list

### 4.4 Settings Module

**Purpose**: Configure application preferences

**User Flow**:
1. User navigates to Settings (Ctrl+4 or click "⚙️ Settings")
2. Configures preferences:
   - Database location
   - Export formats
   - UI preferences
3. Changes are saved automatically

## 5. Technical Specifications

### 5.1 Logging System
- **Configuration**: utils/logger.py
- **Log Level**: DEBUG (configurable in config.py)
- **Log File**: logs/app.log
- **Rotation**: 1MB max size, 3 backup files
- **Format**: timestamp - level - module - message

### 5.2 Database Management
- **Connection**: Singleton pattern via Database class
- **Location**: my_spanish_app.db (configurable)
- **Initialization**: Automatic table creation on startup
- **Foreign Keys**: Enabled for referential integrity

### 5.3 UI Components
- **Framework**: PyQt6 with native OS styling
- **Layout**: Responsive design with QHBoxLayout/QVBoxLayout
- **Navigation**: Sidebar with stacked widget pattern
- **Shortcuts**: 
  - Ctrl+1-4: Navigate between views
  - Ctrl+Q: Quit application
  - F1: Show help

### 5.4 Data Export (utils/export.py)
- **Formats**: CSV, JSON, PDF (planned)
- **Scope**: Sessions, vocabulary, grammar
- **Filtering**: By date range, session status

## 6. Error Handling

### Database Errors
- Connection failures logged and user notified
- Transaction rollback on errors
- Graceful degradation if DB unavailable

### UI Errors
- Input validation on all forms
- User-friendly error messages via QMessageBox
- Non-blocking error notifications

## 7. Performance Considerations

### Database
- Indexed foreign keys for faster joins
- Prepared statements for repeated queries
- Connection pooling (single connection per app instance)

### UI
- Lazy loading of data in views
- Pagination for large result sets (planned)
- Asynchronous operations for long-running tasks (planned)

## 8. Security

### Data Protection
- Local SQLite database (no network exposure)
- No authentication required (single-user application)
- No sensitive data encryption (educational content only)

### Input Validation
- SQL injection prevention via parameterized queries
- Input sanitization for all user entries
- File path validation for exports

## 9. Testing Strategy

### Unit Tests
- Model layer: Database CRUD operations
- Utility functions: Export, logging
- Coverage target: 80%

### Integration Tests
- Database transactions
- UI component interactions
- End-to-end user flows

### Manual Testing
- Cross-platform compatibility (Windows, macOS, Linux)
- UI responsiveness
- Data integrity after operations

## 10. Future Enhancements

### Planned Features
1. **Cloud Sync**: Backup data to cloud storage
2. **Multi-language Support**: Extend beyond Spanish
3. **Analytics Dashboard**: Advanced progress visualization
4. **Spaced Repetition**: Smart review scheduling
5. **Audio Recording**: Pronunciation practice tracking
6. **Teacher Management**: Detailed teacher profiles and ratings
7. **Import/Export**: Support for Anki, Quizlet formats
8. **Mobile Companion**: Sync with mobile app

### Technical Improvements
1. **Async Operations**: Non-blocking database queries
2. **Caching Layer**: Improve performance for frequent queries
3. **Plugin System**: Extensible architecture for add-ons
4. **Theme Support**: Dark mode and custom themes
5. **Accessibility**: Screen reader support, keyboard-only navigation

## 11. Development Guidelines

### Code Style
- PEP 8 compliance
- Type hints for function signatures
- Docstrings for all public methods
- Maximum line length: 100 characters

### Version Control
- Git for source control
- Semantic versioning (MAJOR.MINOR.PATCH)
- Feature branches for new development
- Main branch protection

### Documentation
- README.md for setup instructions
- Inline code comments for complex logic
- API documentation for models
- User manual (planned)

## 12. Deployment

### Development Setup
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run application
poetry run python main.py

# Run tests
poetry run pytest tests/
```

### Production Build
- PyInstaller for standalone executable (planned)
- Platform-specific installers (Windows MSI, macOS DMG, Linux AppImage)
- Auto-update mechanism (planned)

## 13. Support & Maintenance

### Logging & Monitoring
- Application logs in logs/app.log
- Error reporting to file
- Performance metrics (planned)

### Backup Strategy
- Automatic database backups (planned)
- Export reminders for manual backups
- Data recovery tools (planned)

### User Support
- In-app help system (F1)
- Online documentation (planned)
- Community forum (planned)