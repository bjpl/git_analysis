# Changelog

All notable changes to the Unsplash Image Search with GPT application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive distribution documentation
- Automated CI/CD pipeline with GitHub Actions
- Multi-platform build support (Windows, macOS, Linux)
- NSIS installer with custom configuration wizard
- Portable version for USB/standalone deployment
- Package manager support (Chocolatey, Scoop)

### Changed
- Improved build scripts for cross-platform compatibility
- Enhanced error handling during installation
- Updated documentation structure

### Fixed
- Build issues on systems with spaces in paths
- Missing dependencies in portable version

## [2.0.0] - 2024-01-15

### Added
- **Complete UI Overhaul**: New theme system with light/dark mode support
- **Enhanced Image Viewer**: Zoom controls with mouse wheel support
- **Export Functionality**: Multiple format support (Anki, CSV, Plain Text)
- **Vocabulary Management**: Improved vocabulary tracking with context
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Progress Indicators**: Visual feedback during API operations
- **Help System**: Integrated help dialog with shortcuts reference
- **Session Statistics**: Real-time tracking of images viewed and words learned
- **Error Handling**: Enhanced error messages with recovery suggestions
- **Configuration Wizard**: First-run setup wizard for API keys
- **Modular Architecture**: Refactored codebase into maintainable modules

### Enhanced Features
- **Image Cache**: LRU cache for faster image loading
- **API Retry Logic**: Exponential backoff for failed requests
- **Rate Limit Handling**: Intelligent rate limit detection and user feedback
- **Memory Management**: Optimized memory usage for large images
- **Search Persistence**: Remember last search across sessions
- **Vocabulary Deduplication**: Prevent duplicate entries automatically
- **Context-Aware Translation**: Better translations using image context
- **Responsive UI**: Improved layout that adapts to window resizing

### Technical Improvements
- **Modern Python Practices**: Type hints and dataclasses
- **Comprehensive Testing**: Unit, integration, and UI tests
- **Code Quality**: Black formatting, flake8 linting, mypy type checking
- **Security**: Secure API key storage and validation
- **Performance**: Optimized image processing and API calls
- **Documentation**: Complete API and user documentation

### Changed
- **UI Framework**: Upgraded to modern tkinter with themed widgets
- **Configuration System**: New ConfigManager for centralized settings
- **File Structure**: Organized into logical modules (ui/, services/, models/, utils/)
- **Data Format**: JSON-based session logging for better structure
- **Error Reporting**: More descriptive error messages with solutions
- **Build Process**: Streamlined build scripts for multiple platforms

### Fixed
- Image loading issues on high-DPI displays
- Memory leaks during extended usage
- Race conditions in threaded operations
- Unicode handling in vocabulary export
- Window focus issues on macOS
- Path handling on non-Windows systems

### Deprecated
- Legacy text-based configuration format
- Old session log format (still supported for reading)

## [1.5.2] - 2023-12-10

### Fixed
- Critical bug in OpenAI API integration after SDK update
- Memory leak in image caching system
- Crash when handling special characters in search queries

### Security
- Updated dependencies to patch security vulnerabilities
- Improved API key validation and storage

## [1.5.1] - 2023-11-28

### Added
- Support for GPT-4 Turbo model
- Automatic retry mechanism for API failures
- Basic image zoom functionality

### Changed
- Improved error messages for API issues
- Better handling of rate limits
- Updated UI layout for better usability

### Fixed
- Image display issues on Windows 11
- CSV export encoding problems
- Application freeze during network issues

## [1.5.0] - 2023-11-15

### Added
- **GPT-4 Vision Integration**: Upgraded from text-only to vision-capable models
- **Image Analysis**: Direct image analysis instead of text-based descriptions
- **Enhanced Vocabulary**: More accurate phrase extraction from visual context
- **Multiple Export Formats**: CSV, plain text, and basic Anki support
- **Session Logging**: Comprehensive logging of user sessions
- **Configuration Management**: Centralized config system

### Changed
- **API Integration**: Switched to OpenAI Python SDK v1.0+
- **Image Processing**: Improved image handling and display
- **User Interface**: Cleaner layout with better organization
- **Error Handling**: More robust error handling and user feedback

### Fixed
- Compatibility issues with latest OpenAI API
- Image loading failures on slow connections
- UI responsiveness during API calls

## [1.4.3] - 2023-10-20

### Fixed
- Critical security vulnerability in dependency
- Application crash on startup with missing config
- Image caching issues causing excessive memory usage

## [1.4.2] - 2023-10-05

### Added
- Basic theme switching (light/dark mode)
- Image zoom controls
- Keyboard shortcuts for common actions

### Fixed
- Window sizing issues on different screen resolutions
- Vocabulary export with special characters
- API timeout handling

## [1.4.1] - 2023-09-22

### Fixed
- Startup crash on systems without internet connection
- UI freezing during long API operations
- Incorrect vocabulary counting in statistics

### Security
- Improved API key validation
- Enhanced error logging without exposing sensitive data

## [1.4.0] - 2023-09-15

### Added
- **Vocabulary Export**: Export learned vocabulary to CSV format
- **Session Statistics**: Track images viewed and words learned
- **Image Navigation**: "Another Image" and "New Search" functionality
- **Progress Indicators**: Visual feedback during API operations
- **Error Recovery**: Better handling of API failures and network issues

### Improved
- **User Interface**: Cleaner layout and better organization
- **Performance**: Faster image loading and caching
- **Stability**: Reduced crashes and improved error handling

### Fixed
- Memory leaks during extended usage
- Thread safety issues with UI updates
- Incorrect handling of special characters in Spanish text

## [1.3.2] - 2023-08-30

### Fixed
- Critical bug preventing application startup
- API key validation issues
- Image display problems on high-DPI screens

## [1.3.1] - 2023-08-25

### Added
- Support for environment variable configuration
- Basic logging functionality
- Improved error messages

### Fixed
- Configuration file reading on different operating systems
- Unicode handling in API responses
- Application freezing during image downloads

## [1.3.0] - 2023-08-20

### Added
- **Multi-platform Support**: Windows, macOS, and Linux compatibility
- **Configuration System**: External config.ini for API keys and settings
- **Image Caching**: Local cache to reduce API calls and improve performance
- **Vocabulary Tracking**: Automatic tracking of learned Spanish words
- **Translation Feature**: Click-to-translate functionality for Spanish phrases

### Changed
- **Architecture**: Modular design for better maintainability
- **UI Improvements**: Better layout and user experience
- **API Integration**: More robust API handling with retry logic

### Fixed
- Various stability issues and memory leaks
- Image loading problems on slower connections
- UI responsiveness during API operations

## [1.2.1] - 2023-07-15

### Fixed
- Crash when handling empty API responses
- Image display issues with certain file formats
- Configuration loading on first run

### Security
- Improved API key storage security
- Input validation for search queries

## [1.2.0] - 2023-07-10

### Added
- **Spanish Description Generation**: GPT-powered Spanish descriptions of images
- **Phrase Extraction**: Automatic extraction of vocabulary from descriptions
- **Basic UI**: Simple tkinter interface for image search and display
- **API Integration**: Unsplash and OpenAI API integration

### Technical
- Basic error handling for API failures
- Simple configuration management
- Image downloading and display functionality

## [1.1.0] - 2023-06-25

### Added
- **Image Search**: Basic Unsplash API integration
- **Image Display**: Simple image viewer functionality
- **Search Interface**: Basic search input and results display

### Technical
- Core application structure
- Basic API integration framework
- Simple UI layout

## [1.0.0] - 2023-06-15

### Added
- **Initial Release**: Basic application framework
- **Project Setup**: Repository structure and basic documentation
- **Core Dependencies**: Essential libraries and requirements

### Technical
- Python application structure
- Basic configuration system
- Initial UI framework setup

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes or major feature overhauls
- **MINOR**: New features in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

## Release Categories

### Added
New features and functionality

### Changed
Changes to existing functionality

### Deprecated
Soon-to-be removed features

### Removed
Now removed features

### Fixed
Any bug fixes

### Security
Vulnerability fixes and security improvements

## Support Policy

- **Current Version (2.x)**: Full support with regular updates
- **Previous Major (1.x)**: Security fixes only until 2024-06-15
- **Legacy Versions**: No longer supported

## Migration Guides

### Upgrading to 2.0.0

**Configuration Changes**:
- Old `config.ini` format is still supported but deprecated
- New theme settings available in configuration
- API key storage location unchanged

**Data Migration**:
- Session logs automatically converted from text to JSON format
- Vocabulary CSV format enhanced with additional metadata
- Old data files are preserved during upgrade

**UI Changes**:
- New keyboard shortcuts available
- Theme system replaces basic appearance settings  
- Export functionality replaces simple save options

**Breaking Changes**:
- Minimum Python version increased to 3.8+
- Some internal API methods renamed (affects custom integrations)
- Different executable name in some distributions

### Upgrading to 1.5.0

**API Changes**:
- OpenAI API integration updated to v1.0+ SDK
- GPT-4 Vision replaces text-only models
- API key validation more strict

**Data Changes**:
- Session log format changed to JSON
- Vocabulary tracking enhanced with context
- Old session logs preserved but not actively updated

## Known Issues

### Current Version (2.0.0)
- High memory usage with very large images (>10MB)
- Occasional UI freeze on macOS during theme switching
- Export to Anki format requires manual import setup

### Previous Versions
- v1.x: Limited theme support
- v1.4.x and earlier: Memory leaks during extended usage
- v1.3.x and earlier: Thread safety issues

## Future Roadmap

See [ROADMAP.md](../ROADMAP.md) for planned features and improvements.

---

**Note**: This changelog is updated with each release. For the latest changes, see the [Unreleased] section at the top.