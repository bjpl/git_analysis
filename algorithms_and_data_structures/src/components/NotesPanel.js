import React, { useState, useRef, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import NotesList from './NotesList';
import NoteEditor from './NoteEditor';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { exportNotes } from '../utils/notesExport';
import './NotesPanel.css';

const NotesPanel = ({
  lessonId,
  notes = [],
  onNotesChange,
  onCreateNote,
  onUpdateNote,
  onDeleteNote,
  className = '',
  defaultCollapsed = false,
  minWidth = 300,
  maxWidth = 800,
  position = 'right'
}) => {
  const [isCollapsed, setIsCollapsed] = useLocalStorage(`notes-panel-collapsed-${lessonId}`, defaultCollapsed);
  const [panelWidth, setPanelWidth] = useLocalStorage(`notes-panel-width-${lessonId}`, 400);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [isCreatingNote, setIsCreatingNote] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [selectedNotes, setSelectedNotes] = useState([]);
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const panelRef = useRef(null);
  const resizerRef = useRef(null);
  const isDragging = useRef(false);

  // Filter notes based on search and tags
  const filteredNotes = React.useMemo(() => {
    if (!notes.length) return [];

    return notes.filter(note => {
      // Search filter
      const searchMatch = !searchQuery || 
        note.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (note.title && note.title.toLowerCase().includes(searchQuery.toLowerCase()));
      
      // Tag filter
      const tagMatch = selectedTags.length === 0 || 
        selectedTags.every(tag => note.tags && note.tags.includes(tag));
      
      return searchMatch && tagMatch;
    });
  }, [notes, searchQuery, selectedTags]);

  // Get all unique tags
  const availableTags = React.useMemo(() => {
    const tagSet = new Set();
    notes.forEach(note => {
      if (note.tags) {
        note.tags.forEach(tag => tagSet.add(tag));
      }
    });
    return Array.from(tagSet).sort();
  }, [notes]);

  // Handle panel resize
  const handleResizeStart = useCallback((e) => {
    e.preventDefault();
    isDragging.current = true;
    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', handleResizeEnd);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, []);

  const handleResize = useCallback((e) => {
    if (!isDragging.current || !panelRef.current) return;
    
    const rect = panelRef.current.getBoundingClientRect();
    const newWidth = position === 'right' 
      ? rect.right - e.clientX
      : e.clientX - rect.left;
    
    const clampedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    setPanelWidth(clampedWidth);
  }, [position, minWidth, maxWidth, setPanelWidth]);

  const handleResizeEnd = useCallback(() => {
    isDragging.current = false;
    document.removeEventListener('mousemove', handleResize);
    document.removeEventListener('mouseup', handleResizeEnd);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, [handleResize]);

  // Cleanup resize listeners
  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleResize);
      document.removeEventListener('mouseup', handleResizeEnd);
    };
  }, [handleResize, handleResizeEnd]);

  // Handle search
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  // Handle tag filter
  const handleTagToggle = (tag) => {
    setSelectedTags(prev => 
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  // Clear all filters
  const clearFilters = () => {
    setSearchQuery('');
    setSelectedTags([]);
  };

  // Handle note creation
  const handleCreateNote = () => {
    setIsCreatingNote(true);
    setEditingNote(null);
  };

  // Handle note save
  const handleNoteSave = async (content) => {
    try {
      if (editingNote) {
        await onUpdateNote?.(editingNote.id, { ...editingNote, content });
        setEditingNote(null);
      } else {
        await onCreateNote?.({
          content,
          lessonId,
          timestamp: new Date().toISOString(),
          tags: []
        });
        setIsCreatingNote(false);
      }
    } catch (error) {
      console.error('Failed to save note:', error);
      // You might want to show an error message here
    }
  };

  // Handle note editing
  const handleNoteEdit = (note) => {
    setEditingNote(note);
    setIsCreatingNote(false);
  };

  // Handle cancel editing
  const handleCancelEdit = () => {
    setEditingNote(null);
    setIsCreatingNote(false);
  };

  // Handle export
  const handleExport = async () => {
    try {
      await exportNotes(filteredNotes, {
        format: 'markdown',
        includeMetadata: true,
        lessonId
      });
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Handle sort change
  const handleSortChange = (newSortBy, newSortOrder) => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
  };

  return (
    <div 
      ref={panelRef}
      className={`notes-panel ${position} ${isCollapsed ? 'collapsed' : ''} ${className}`}
      style={{
        width: isCollapsed ? 'auto' : `${panelWidth}px`,
        minWidth: isCollapsed ? 'auto' : `${minWidth}px`,
        maxWidth: isCollapsed ? 'auto' : `${maxWidth}px`
      }}
      role="complementary"
      aria-label="Notes panel"
    >
      {/* Resizer */}
      {!isCollapsed && (
        <div
          ref={resizerRef}
          className={`panel-resizer ${position}`}
          onMouseDown={handleResizeStart}
          role="separator"
          aria-label="Resize notes panel"
          aria-orientation="vertical"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
              e.preventDefault();
              const delta = e.key === 'ArrowLeft' ? -20 : 20;
              const newWidth = position === 'right' 
                ? panelWidth + (e.key === 'ArrowLeft' ? delta : -delta)
                : panelWidth + delta;
              const clampedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
              setPanelWidth(clampedWidth);
            }
          }}
        />
      )}

      {/* Header */}
      <div className="notes-panel__header">
        <button
          type="button"
          className="panel-toggle"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label={isCollapsed ? 'Expand notes panel' : 'Collapse notes panel'}
          title={isCollapsed ? 'Expand notes' : 'Collapse notes'}
        >
          {isCollapsed ? '▶' : '◀'}
        </button>
        
        {!isCollapsed && (
          <>
            <h2 className="panel-title">Notes</h2>
            <div className="header-actions">
              <button
                type="button"
                className="action-btn create-note"
                onClick={handleCreateNote}
                disabled={isCreatingNote || editingNote}
                aria-label="Create new note"
                title="Create new note"
              >
                +
              </button>
              <button
                type="button"
                className="action-btn export-notes"
                onClick={handleExport}
                disabled={!filteredNotes.length}
                aria-label="Export notes"
                title="Export notes"
              >
                ↓
              </button>
            </div>
          </>
        )}
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="notes-panel__content">
          {/* Search and Filters */}
          <div className="search-section">
            <div className="search-input-wrapper">
              <input
                type="text"
                className="search-input"
                placeholder="Search notes..."
                value={searchQuery}
                onChange={handleSearchChange}
                aria-label="Search notes"
              />
              {searchQuery && (
                <button
                  type="button"
                  className="clear-search"
                  onClick={() => setSearchQuery('')}
                  aria-label="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
            
            {/* Tag filters */}
            {availableTags.length > 0 && (
              <div className="tag-filters">
                <div className="tag-filter-label">Filter by tags:</div>
                <div className="tag-buttons">
                  {availableTags.map(tag => (
                    <button
                      key={tag}
                      type="button"
                      className={`tag-filter ${selectedTags.includes(tag) ? 'active' : ''}`}
                      onClick={() => handleTagToggle(tag)}
                      aria-label={`${selectedTags.includes(tag) ? 'Remove' : 'Add'} ${tag} filter`}
                    >
                      #{tag}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Clear filters */}
            {(searchQuery || selectedTags.length > 0) && (
              <button
                type="button"
                className="clear-filters"
                onClick={clearFilters}
                aria-label="Clear all filters"
              >
                Clear filters
              </button>
            )}
          </div>

          {/* Editor */}
          {(isCreatingNote || editingNote) && (
            <div className="editor-section">
              <NoteEditor
                note={editingNote}
                onSave={handleNoteSave}
                onCancel={handleCancelEdit}
                placeholder={isCreatingNote ? "Start writing your note..." : "Edit your note..."}
                autoSave={false}
              />
            </div>
          )}

          {/* Notes List */}
          {!isCreatingNote && !editingNote && (
            <div className="notes-section">
              <NotesList
                notes={filteredNotes}
                onNoteEdit={handleNoteEdit}
                onNoteDelete={onDeleteNote}
                onNotesSelect={setSelectedNotes}
                selectedNotes={selectedNotes}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSortChange={handleSortChange}
                emptyMessage={notes.length === 0 
                  ? "No notes yet. Create your first note!" 
                  : "No notes match your filters."}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

NotesPanel.propTypes = {
  lessonId: PropTypes.string.isRequired,
  notes: PropTypes.array,
  onNotesChange: PropTypes.func,
  onCreateNote: PropTypes.func,
  onUpdateNote: PropTypes.func,
  onDeleteNote: PropTypes.func,
  className: PropTypes.string,
  defaultCollapsed: PropTypes.bool,
  minWidth: PropTypes.number,
  maxWidth: PropTypes.number,
  position: PropTypes.oneOf(['left', 'right'])
};

export default NotesPanel;