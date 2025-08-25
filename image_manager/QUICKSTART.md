# Image Manager - Quick Start Guide

## Installation
```bash
pip install -r requirements.txt
python image_manager.py
```

## Keyboard Shortcuts

### Navigation
- **←/→** Arrow keys: Previous/Next image
- **Page Up/Down**: Scroll grid view
- **Ctrl+F**: Focus search box
- **F5**: Start slideshow
- **Space**: Next image (in slideshow)
- **ESC**: Stop slideshow/Cancel operation

### Image Operations
- **F2**: Rename current image
- **Delete**: Remove from catalog
- **F**: Toggle favorite
- **Ctrl+R**: Batch rename
- **Ctrl+Z**: Undo last delete

### Selection (Grid View)
- **Ctrl+Click**: Multi-select images
- **Ctrl+A**: Select all visible
- **Ctrl+D**: Deselect all

### Zoom (Detail View)
- **+**: Zoom in
- **-**: Zoom out
- **0**: Reset zoom

## Quick Tips

1. **First Run**: The app will prompt you to scan a folder or add individual images

2. **Batch Operations**: 
   - Select multiple images with Ctrl+Click
   - Click "📦 Batch" button for bulk operations (tags, move, copy, rating)

3. **Smart Filters**:
   - "Favorites Only" - Show starred images
   - "Untagged Only" - Find images without tags
   - Min Rating - Filter by star rating

4. **Export Images**:
   - File → Export Images
   - Options to preserve folder structure
   - Export tags to text file

5. **Performance**:
   - Grid shows first 100 images (use search to see more)
   - Thumbnails are cached for speed
   - Large scans run in background

6. **Organization**:
   - Right-click thumbnails for context menu
   - Create collections to group related images
   - Tags are searchable and persistent

## File Safety
- Delete only removes from catalog, NOT from disk
- Move/Copy operations have overwrite warnings
- Ctrl+Z undoes deletions
- Invalid filenames are blocked

## Common Workflows

### Organize Vacation Photos
1. Scan your vacation folder
2. Use batch rename: `vacation_{num:04d}`
3. Tag with location names
4. Create a collection "Summer 2024"
5. Export favorites to share

### Find and Tag Unorganized Images
1. Use "Untagged Only" filter
2. Select similar images (Ctrl+Click)
3. Click "📦 Batch" → Add tags
4. Rate your best photos
5. Mark favorites with F key

### Create Photo Slideshow
1. Filter to show favorites
2. Press F5 to start slideshow
3. Adjust delay in control window
4. Press Space to advance manually
5. ESC to stop

## Troubleshooting

- **Images not loading**: Check file exists and isn't corrupted
- **Slow performance**: Reduce thumbnail size in config.json
- **Can't see all images**: Grid limited to 100, use search
- **Scan seems stuck**: Check status bar, large folders take time