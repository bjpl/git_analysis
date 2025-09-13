# Note-Taking UI Components

A comprehensive set of React components for building note-taking applications with rich text editing, markdown support, and advanced features.

## Components Overview

### Core Components
- **NoteEditor**: Rich text editor with markdown support and auto-save
- **NotesList**: Display and manage multiple notes with sorting and filtering
- **NotesPanel**: Main container with collapsible interface and search
- **NoteCard**: Individual note display with preview and actions

## Quick Start

```jsx
import React, { useState } from 'react';
import { NotesPanel } from './components/NotesPanel';

const App = () => {
  const [notes, setNotes] = useState([]);
  
  const handleCreateNote = (noteData) => {
    const newNote = {
      id: Date.now().toString(),
      ...noteData,
      timestamp: new Date().toISOString()
    };
    setNotes(prev => [newNote, ...prev]);
  };
  
  const handleUpdateNote = (noteId, updates) => {
    setNotes(prev => prev.map(note => 
      note.id === noteId ? { ...note, ...updates } : note
    ));
  };
  
  const handleDeleteNote = (noteId) => {
    setNotes(prev => prev.filter(note => note.id !== noteId));
  };
  
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <main style={{ flex: 1 }}>
        {/* Your main content here */}
      </main>
      
      <NotesPanel
        lessonId="lesson-1"
        notes={notes}
        onCreateNote={handleCreateNote}
        onUpdateNote={handleUpdateNote}
        onDeleteNote={handleDeleteNote}
        position="right"
        defaultCollapsed={false}
      />
    </div>
  );
};

export default App;
```

## Component Details

### NoteEditor

Rich text editor with markdown support, auto-save, and formatting toolbar.

```jsx
import { NoteEditor } from './components/NoteEditor';

<NoteEditor
  note={editingNote}
  onSave={handleSave}
  onCancel={handleCancel}
  autoSave={true}
  placeholder="Start writing your notes..."
  maxLength={10000}
/>
```

**Props:**
- `note`: Note object to edit
- `onSave`: Function called when saving (required)
- `onCancel`: Function called when canceling
- `autoSave`: Enable auto-save (default: true)
- `placeholder`: Placeholder text
- `maxLength`: Maximum character length (default: 10000)

**Features:**
- Rich text editing with markdown support
- Auto-save with debouncing
- Character/word count
- Formatting toolbar (bold, italic, headings, lists)
- Keyboard shortcuts (Ctrl+B, Ctrl+I, Ctrl+S)
- Accessibility support

### NotesList

Display and manage collections of notes with advanced filtering and sorting.

```jsx
import { NotesList } from './components/NotesList';

<NotesList
  notes={filteredNotes}
  onNoteEdit={handleEdit}
  onNoteDelete={handleDelete}
  onNotesSelect={setSelectedNotes}
  selectedNotes={selectedNotes}
  sortBy="date"
  sortOrder="desc"
  onSortChange={handleSortChange}
/>
```

**Props:**
- `notes`: Array of note objects
- `onNoteEdit`: Function called when editing a note
- `onNoteDelete`: Function called when deleting a note
- `onNotesSelect`: Function called when selecting notes
- `selectedNotes`: Array of selected note IDs
- `sortBy`: Sort field ('date', 'title', 'content', 'relevance')
- `sortOrder`: Sort order ('asc', 'desc')
- `onSortChange`: Function called when sort changes

**Features:**
- Grid layout with responsive design
- Multiple sorting options
- Bulk selection and operations
- Hover previews
- Loading and empty states
- Statistics display

### NotesPanel

Main container component with search, filtering, and collapsible interface.

```jsx
import { NotesPanel } from './components/NotesPanel';

<NotesPanel
  lessonId="lesson-1"
  notes={notes}
  onCreateNote={handleCreate}
  onUpdateNote={handleUpdate}
  onDeleteNote={handleDelete}
  position="right"
  minWidth={300}
  maxWidth={800}
  defaultCollapsed={false}
/>
```

**Props:**
- `lessonId`: Unique identifier for the lesson (required)
- `notes`: Array of note objects
- `onCreateNote`: Function called when creating a note
- `onUpdateNote`: Function called when updating a note
- `onDeleteNote`: Function called when deleting a note
- `position`: Panel position ('left', 'right')
- `minWidth`: Minimum panel width (default: 300)
- `maxWidth`: Maximum panel width (default: 800)
- `defaultCollapsed`: Initial collapsed state

**Features:**
- Collapsible/resizable panel
- Search and tag filtering
- Note creation and editing
- Export functionality
- Persistent state (localStorage)
- Responsive design

### NoteCard

Individual note display with preview, actions, and metadata.

```jsx
import { NoteCard } from './components/NoteCard';

<NoteCard
  note={note}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onSelect={handleSelect}
  isSelected={isSelected}
  selectionMode={selectionMode}
/>
```

**Props:**
- `note`: Note object (required)
- `onEdit`: Function called when editing
- `onDelete`: Function called when deleting  
- `onSelect`: Function called when selecting
- `isSelected`: Whether note is selected
- `selectionMode`: Whether in selection mode
- `maxPreviewLength`: Maximum preview text length (default: 150)

**Features:**
- Rich preview with auto-generated titles
- Context menu with actions
- Tag display
- Timestamp formatting
- Status indicators
- Extended preview on hover
- Keyboard navigation

## Data Structure

### Note Object

```typescript
interface Note {
  id: string;                    // Unique identifier
  content: string;               // Note content (markdown)
  title?: string;               // Optional title
  timestamp: string | Date;      // Creation/modification time
  lessonId?: string;            // Associated lesson
  tags?: string[];              // Tags for categorization
  wordCount?: number;           // Word count
  isBookmarked?: boolean;       // Bookmark status
  hasReminder?: boolean;        // Reminder status
  isShared?: boolean;           // Share status
  relevanceScore?: number;      // Search relevance
}
```

## Styling and Themes

All components support both light and dark themes automatically through CSS custom properties and media queries.

### Theme Variables

```css
/* Light theme (default) */
--bg-primary: #ffffff;
--bg-secondary: #f8f9fa;
--text-primary: #333333;
--text-secondary: #666666;
--border-color: #e1e5e9;
--primary-color: #1a73e8;

/* Dark theme (prefers-color-scheme: dark) */
--bg-primary: #1a1a1a;
--bg-secondary: #2a2a2a;
--text-primary: #ffffff;
--text-secondary: #cccccc;
--border-color: #404040;
--primary-color: #4285f4;
```

### Manual Theme Classes

```jsx
<NotesPanel className="theme-dark" />
<NotesPanel className="theme-light" />
```

## Accessibility Features

- Full keyboard navigation support
- ARIA labels and roles
- Screen reader compatibility
- High contrast mode support
- Focus management
- Semantic HTML structure

## Responsive Design

- Mobile-first approach
- Flexible grid layouts
- Touch-friendly interfaces
- Collapsible panels on small screens
- Optimized for tablets and phones

## Browser Support

- Chrome/Chromium 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Performance Optimizations

- Virtualized lists for large datasets
- Debounced search and auto-save
- Lazy loading of components
- Memoized calculations
- Efficient re-rendering

## Utilities and Hooks

### useLocalStorage Hook

```jsx
import { useLocalStorage } from '../hooks/useLocalStorage';

const [value, setValue] = useLocalStorage('key', defaultValue);
```

### Helper Functions

```jsx
import { 
  truncateText,
  formatTimestamp,
  countWords,
  debounce 
} from '../utils/helpers';
```

### Export Functions

```jsx
import { exportNotes, copyNotesToClipboard } from '../utils/notesExport';

// Export as markdown
await exportNotes(notes, { format: 'markdown' });

// Copy to clipboard
await copyNotesToClipboard(notes, 'markdown');
```

## Examples

### Basic Implementation

```jsx
import React, { useState, useEffect } from 'react';
import { NotesPanel } from './components/NotesPanel';

const LearningApp = () => {
  const [notes, setNotes] = useState([]);
  const [currentLesson, setCurrentLesson] = useState('intro-to-algorithms');
  
  // Load notes for current lesson
  useEffect(() => {
    loadNotesForLesson(currentLesson);
  }, [currentLesson]);
  
  const loadNotesForLesson = async (lessonId) => {
    try {
      const lessonNotes = await fetchNotes(lessonId);
      setNotes(lessonNotes);
    } catch (error) {
      console.error('Failed to load notes:', error);
    }
  };
  
  return (
    <div className="learning-app">
      <main className="lesson-content">
        {/* Lesson content here */}
      </main>
      
      <NotesPanel
        lessonId={currentLesson}
        notes={notes}
        onCreateNote={async (noteData) => {
          const saved = await saveNote(noteData);
          setNotes(prev => [saved, ...prev]);
        }}
        onUpdateNote={async (noteId, updates) => {
          await updateNote(noteId, updates);
          setNotes(prev => prev.map(note => 
            note.id === noteId ? { ...note, ...updates } : note
          ));
        }}
        onDeleteNote={async (noteId) => {
          await deleteNote(noteId);
          setNotes(prev => prev.filter(note => note.id !== noteId));
        }}
      />
    </div>
  );
};
```

### Advanced Features

```jsx
import React, { useState, useMemo } from 'react';
import { NotesPanel, NoteEditor, NotesList } from './components';

const AdvancedNotesApp = () => {
  const [notes, setNotes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  
  // Filter notes based on search and tags
  const filteredNotes = useMemo(() => {
    return notes.filter(note => {
      const matchesSearch = !searchQuery || 
        note.content.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesTags = selectedTags.length === 0 || 
        selectedTags.every(tag => note.tags?.includes(tag));
      
      return matchesSearch && matchesTags;
    });
  }, [notes, searchQuery, selectedTags]);
  
  // Auto-tag notes based on content
  const autoTagNote = (content) => {
    const tags = [];
    if (content.includes('algorithm')) tags.push('algorithms');
    if (content.includes('data structure')) tags.push('data-structures');
    if (content.includes('complexity')) tags.push('complexity');
    return tags;
  };
  
  const handleCreateNote = (noteData) => {
    const newNote = {
      ...noteData,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      tags: autoTagNote(noteData.content),
      wordCount: noteData.content.split(/\s+/).length
    };
    
    setNotes(prev => [newNote, ...prev]);
  };
  
  return (
    <NotesPanel
      lessonId="advanced-algorithms"
      notes={filteredNotes}
      onCreateNote={handleCreateNote}
      // ... other props
    />
  );
};
```

## Contributing

Please follow the existing patterns and ensure all components:
- Include comprehensive PropTypes
- Support accessibility features
- Follow responsive design principles
- Include proper error handling
- Maintain performance optimizations

## License

MIT License - see LICENSE file for details.