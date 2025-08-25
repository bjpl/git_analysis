# Image Manager - Browse, Label & Organize

A powerful desktop application for managing, labeling, and organizing images across your system.

## Features

### Core Functionality
- **Image Discovery**: Scan directories recursively to find all images
- **Multi-format Support**: JPG, PNG, GIF, BMP, TIFF, WebP, ICO, SVG
- **SQLite Database**: Fast, persistent catalog of all your images

### Views
- **Grid View**: Thumbnail grid for quick browsing
- **Detail View**: Large preview with full metadata
- **List View**: Compact listing (planned)

### Organization
- **Tags**: Add unlimited tags to categorize images
- **Collections**: Group images into named collections
- **Ratings**: 0-5 star rating system
- **Favorites**: Quick marking for special images

### Image Management
- **Move/Copy**: Relocate or duplicate images while maintaining catalog
- **Batch Operations**: Tag multiple images at once
- **Search & Filter**: Find images by name, tags, rating, or favorite status
- **Duplicate Detection**: Find similar images (planned)

### User Interface
- **Dark Theme**: Easy on the eyes for extended use
- **Keyboard Shortcuts**:
  - Arrow keys: Navigate images
  - F: Toggle favorite
  - Delete: Remove from catalog
  - Ctrl+F: Focus search

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python image_manager.py
```

### Getting Started
1. **Add Images**: Use File → Scan Directory to import images
2. **Browse**: Click thumbnails in grid view or use arrow keys
3. **Organize**: Add tags, ratings, and create collections
4. **Search**: Use the search bar to find specific images

### Tips
- Double-click thumbnails to open in default image viewer
- Scan large directories in background while continuing to work
- Create collections for projects, themes, or events
- Use batch tagging for efficient organization

## Database

The application creates `image_catalog.db` in the application directory. This SQLite database contains:
- Image metadata (path, size, dimensions)
- Tags and collections
- Ratings and favorites
- Custom notes

## Performance

- Thumbnails are generated on-demand and cached
- Background scanning for non-blocking imports
- Efficient SQLite queries for fast searching
- Lazy loading for large image collections

## Future Enhancements

- Export collections to folders/archives
- Advanced duplicate detection with perceptual hashing
- Facial recognition and auto-tagging
- Cloud storage integration
- Image editing tools
- Slideshow mode
- Metadata EXIF reading/writing

## Requirements

- Python 3.8+
- Tkinter (included with Python)
- Pillow (PIL) for image processing
- SQLite3 (included with Python)