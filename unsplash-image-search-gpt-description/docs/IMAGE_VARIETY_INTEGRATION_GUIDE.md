# Image Variety Integration Guide

This guide explains how to integrate the new image variety and session tracking features into the existing UnsplashGPT application.

## Overview

The image variety system provides:

1. **Session-aware image tracking** - Remembers previously shown images
2. **Intelligent page rotation** - Uses different API pages for repeated searches  
3. **Time-based randomization** - Adds entropy to search results
4. **Shuffle functionality** - Provides immediate variety on demand
5. **Fresh search option** - Resets history for completely new results
6. **Session analytics** - Tracks usage patterns and search statistics

## Quick Integration

### Step 1: Import the Integration Module

```python
from src.features.image_variety_integration import integrate_image_variety

# In your main application initialization:
def __init__(self):
    # ... existing initialization ...
    
    # Add image variety features
    self.variety_manager = integrate_image_variety(
        main_app=self, 
        data_dir=Path('./data/sessions')
    )
```

### Step 2: The Integration is Automatic

The `integrate_image_variety()` function automatically:

- ✅ Adds shuffle and fresh search buttons to your UI
- ✅ Wraps your existing search methods with variety logic
- ✅ Adds query statistics display
- ✅ Manages session persistence
- ✅ Enables/disables controls appropriately

### Step 3: Optional Session Management

```python
# Save session when app closes
def on_closing(self):
    if hasattr(self, 'variety_manager'):
        self.variety_manager.save_session()
    self.root.destroy()

# Get session statistics for display
def show_session_stats(self):
    if hasattr(self, 'variety_manager'):
        stats = self.variety_manager.get_session_summary()
        print(f"Images viewed: {stats['images_viewed']}")
        print(f"Unique searches: {stats['unique_searches']}")
```

## Manual Integration (Advanced)

If you prefer more control, you can integrate the components manually:

### Step 1: Create Session Tracker

```python
from src.features.enhanced_session_tracker import EnhancedSessionTracker

# In your main app initialization
self.session_tracker = EnhancedSessionTracker(Path('./data/sessions'))
```

### Step 2: Enhance Your Search Method

```python
def search_images(self):
    query = self.search_entry.get().strip()
    if not query:
        messagebox.showerror("Error", "Please enter a search term.")
        return
    
    # Get variety-enhanced search parameters
    from src.features.enhanced_session_tracker import get_image_search_parameters
    search_params = get_image_search_parameters(self.session_tracker, query)
    
    # Use enhanced parameters in your API call
    self.current_page = search_params['page']
    self.current_query = query
    
    # Continue with your existing search logic...
```

### Step 3: Track Shown Images

```python
def display_image(self, photo, pil_image=None):
    # Your existing display logic...
    
    # Track the image
    if hasattr(self, 'session_tracker') and self.current_query:
        # Extract image ID from your image data
        image_id = self.get_current_image_id()  # Your method to get image ID
        image_url = self.current_image_url
        
        self.session_tracker.record_image_shown(
            self.current_query, 
            image_id, 
            image_url, 
            self.current_page
        )
```

### Step 4: Add Shuffle Button

```python
def add_shuffle_button(self):
    self.shuffle_button = ttk.Button(
        self.control_frame,
        text="🔀 Shuffle",
        command=self.shuffle_images
    )
    self.shuffle_button.pack(side='left', padx=2)

def shuffle_images(self):
    query = self.search_entry.get().strip()
    if not query:
        return
    
    # Get shuffled parameters
    page, offset = self.session_tracker.shuffle_search(query)
    
    # Perform search with shuffled parameters
    self.search_with_params(query, page, offset, shuffle=True)
```

## API Integration Examples

### Enhanced Unsplash API Call

```python
def build_search_url(self, query, use_variety=True):
    base_url = f"https://api.unsplash.com/search/photos?query={query}"
    
    if use_variety and hasattr(self, 'session_tracker'):
        # Get variety parameters
        search_params = get_image_search_parameters(self.session_tracker, query)
        
        # Add variety to URL
        url = (f"{base_url}&"
               f"page={search_params['page']}&"
               f"per_page={search_params['per_page']}&"
               f"order_by={search_params['order_by']}")
        
        # Apply offset by skipping results
        self.result_offset = search_params.get('query_offset', 0)
        
        return url
    
    return f"{base_url}&page=1&per_page=10"
```

### Filter Previously Seen Images

```python
def filter_results(self, results, query):
    """Remove previously seen images from results."""
    if not hasattr(self, 'session_tracker'):
        return results
    
    filtered = []
    for result in results:
        image_id = result.get('id')
        if not self.session_tracker.has_seen_image(query, image_id):
            filtered.append(result)
        
        # Limit to reasonable number
        if len(filtered) >= 10:
            break
    
    # If no new images, use subset of original
    return filtered if filtered else results[:5]
```

## UI Enhancement Examples

### Add Query Statistics Display

```python
def add_stats_display(self):
    self.stats_label = ttk.Label(
        self.stats_frame,
        text="",
        font=('Arial', 8)
    )
    self.stats_label.pack(side='right')

def update_query_stats(self, query):
    if hasattr(self, 'session_tracker'):
        stats = self.session_tracker.get_query_stats(query)
        stats_text = f"Page {stats['current_page']} | {stats['images_shown']} seen"
        self.stats_label.config(text=stats_text)
```

### Add Fresh Search Button

```python
def add_fresh_search_button(self):
    self.fresh_button = ttk.Button(
        self.control_frame,
        text="🆕 Fresh Search",
        command=self.fresh_search
    )
    self.fresh_button.pack(side='left', padx=2)

def fresh_search(self):
    query = self.search_entry.get().strip()
    if not query:
        return
    
    # Reset query history
    if hasattr(self, 'session_tracker'):
        self.session_tracker.reset_query_history(query)
    
    # Perform fresh search
    self.search_images()
```

## Configuration Options

### Session Tracker Configuration

```python
# Create tracker with custom settings
self.session_tracker = EnhancedSessionTracker(
    data_dir=Path('./data/sessions'),
)

# Configure variety manager
self.session_tracker.current_session.search_variety_manager.max_history = 100
self.session_tracker.current_session.search_variety_manager.session_memory_hours = 48
```

### Search Parameter Customization

```python
def get_custom_search_params(self, query, shuffle=False):
    if shuffle:
        page, offset = self.session_tracker.shuffle_search(query)
    else:
        page, offset = self.session_tracker.get_search_parameters(query)
    
    return {
        'page': page,
        'per_page': 15,  # Custom page size
        'order_by': 'popular' if shuffle else 'relevant',
        'orientation': 'landscape',  # Custom orientation
        'content_filter': 'high',
        'query_offset': offset
    }
```

## Data Management

### Export Session Data

```python
def export_session_data(self):
    if hasattr(self, 'variety_manager'):
        # Export search history
        history_file = self.variety_manager.export_search_history()
        print(f"Search history exported to: {history_file}")
        
        # Export quiz/session data
        attempts_file = self.variety_manager.session_tracker.export_attempts_for_analysis()
        print(f"Session data exported to: {attempts_file}")
```

### Session Statistics

```python
def show_detailed_stats(self):
    if hasattr(self, 'variety_manager'):
        current_stats = self.variety_manager.get_session_summary()
        overall_stats = self.variety_manager.session_tracker.get_overall_stats()
        
        print("=== Current Session ===")
        print(f"Images viewed: {current_stats['images_viewed']}")
        print(f"Unique searches: {current_stats['unique_searches']}")
        
        print("\\n=== Overall Statistics ===")  
        print(f"Total sessions: {overall_stats['total_sessions']}")
        print(f"Total images: {overall_stats['total_images_viewed']}")
        print(f"Total searches: {overall_stats['total_unique_searches']}")
```

## Testing Your Integration

### Run the Demo

```bash
python examples/image_variety_demo.py
```

### Run the Tests

```bash
python -m pytest tests/test_image_variety.py -v
```

### Manual Testing Checklist

- [ ] Search for the same term multiple times - should show different images
- [ ] Use the shuffle button - should show different images immediately
- [ ] Use fresh search - should reset history and start over
- [ ] Check query statistics update correctly
- [ ] Verify session persistence across app restarts
- [ ] Test with various search terms and patterns

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure `src` is in your Python path
2. **File Permissions**: Ensure write access to the data directory
3. **Memory Usage**: Large search histories use more memory - adjust `max_history`
4. **API Rate Limits**: Variety features may increase API calls - implement rate limiting

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# The session tracker will print debug information
```

### Reset Everything

```python
# Clear all session data
if hasattr(self, 'variety_manager'):
    import shutil
    shutil.rmtree(self.variety_manager.data_dir, ignore_errors=True)
    self.variety_manager.data_dir.mkdir(exist_ok=True)
```

## Performance Considerations

- Search history is cleaned up automatically (default: 24 hours)
- Maximum history size is limited (default: 50 records)
- JSON files are small and load quickly
- Session tracking adds minimal overhead

## Next Steps

1. Run the demo to see features in action
2. Run tests to verify functionality
3. Integrate using the automatic method first
4. Customize as needed for your specific use case
5. Add additional UI elements for better user experience

The image variety system is designed to be backward-compatible and non-intrusive. Your existing functionality will continue to work while gaining the benefits of intelligent image rotation and session tracking.