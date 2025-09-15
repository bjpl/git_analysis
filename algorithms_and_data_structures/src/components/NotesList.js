import React, { useState, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import NoteCard from './NoteCard';
import './NotesList.css';

const NotesList = ({
  notes = [],
  onNoteEdit,
  onNoteDelete,
  onNotesSelect,
  selectedNotes = [],
  sortBy = 'date',
  sortOrder = 'desc',
  onSortChange,
  className = '',
  loading = false,
  emptyMessage = "No notes yet. Create your first note!"
}) => {
  const [hoveredNoteId, setHoveredNoteId] = useState(null);
  const [isSelectionMode, setIsSelectionMode] = useState(false);

  // Sort and filter notes
  const sortedNotes = useMemo(() => {
    if (!notes.length) return [];

    const sorted = [...notes].sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(b.timestamp) - new Date(a.timestamp);
          break;
        case 'title':
          comparison = (a.title || '').localeCompare(b.title || '');
          break;
        case 'content':
          comparison = (a.content || '').length - (b.content || '').length;
          break;
        case 'relevance':
          comparison = (b.relevanceScore || 0) - (a.relevanceScore || 0);
          break;
        default:
          comparison = 0;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    
    return sorted;
  }, [notes, sortBy, sortOrder]);

  // Handle sort change
  const handleSortChange = (newSortBy) => {
    const newSortOrder = sortBy === newSortBy && sortOrder === 'desc' ? 'asc' : 'desc';
    onSortChange?.(newSortBy, newSortOrder);
  };

  // Handle note selection
  const handleNoteSelect = useCallback((noteId, isSelected) => {
    const newSelection = isSelected
      ? [...selectedNotes, noteId]
      : selectedNotes.filter(id => id !== noteId);
    onNotesSelect?.(newSelection);
  }, [selectedNotes, onNotesSelect]);

  // Handle select all/none
  const handleSelectAll = () => {
    const allSelected = selectedNotes.length === sortedNotes.length;
    const newSelection = allSelected ? [] : sortedNotes.map(note => note.id);
    onNotesSelect?.(newSelection);
  };

  // Handle bulk delete
  const handleBulkDelete = () => {
    if (selectedNotes.length > 0 && onNoteDelete) {
      selectedNotes.forEach(noteId => onNoteDelete(noteId));
      setIsSelectionMode(false);
    }
  };

  // Toggle selection mode
  const toggleSelectionMode = () => {
    setIsSelectionMode(!isSelectionMode);
    if (isSelectionMode) {
      onNotesSelect?.([]);
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && isSelectionMode) {
      setIsSelectionMode(false);
      onNotesSelect?.([]);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className={`notes-list loading ${className}`} role="status" aria-label="Loading notes">
        <div className="loading-spinner" />
        <p>Loading notes...</p>
      </div>
    );
  }

  // Empty state
  if (!sortedNotes.length) {
    return (
      <div className={`notes-list empty ${className}`} role="status">
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <p className="empty-message">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`notes-list ${className}`} 
      onKeyDown={handleKeyDown}
      role="region"
      aria-label="Notes list"
    >
      {/* Header with controls */}
      <div className="notes-list__header">
        <div className="notes-count" aria-live="polite">
          {sortedNotes.length} note{sortedNotes.length !== 1 ? 's' : ''}
          {selectedNotes.length > 0 && (
            <span className="selected-count">
              ({selectedNotes.length} selected)
            </span>
          )}
        </div>
        
        <div className="notes-controls">
          {/* Sort dropdown */}
          <div className="sort-control">
            <label htmlFor="sort-select" className="sr-only">Sort notes by</label>
            <select
              id="sort-select"
              className="sort-select"
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [newSortBy, newSortOrder] = e.target.value.split('-');
                onSortChange?.(newSortBy, newSortOrder);
              }}
              aria-label="Sort notes"
            >
              <option value="date-desc">Latest first</option>
              <option value="date-asc">Oldest first</option>
              <option value="title-asc">Title A-Z</option>
              <option value="title-desc">Title Z-A</option>
              <option value="content-desc">Longest first</option>
              <option value="content-asc">Shortest first</option>
              <option value="relevance-desc">Most relevant</option>
            </select>
          </div>
          
          {/* Bulk actions */}
          <button
            type="button"
            className={`selection-toggle ${isSelectionMode ? 'active' : ''}`}
            onClick={toggleSelectionMode}
            aria-label={isSelectionMode ? 'Exit selection mode' : 'Enter selection mode'}
            title={isSelectionMode ? 'Cancel selection' : 'Select multiple notes'}
          >
            {isSelectionMode ? '✕' : '✓'}
          </button>
        </div>
      </div>

      {/* Bulk action bar */}
      {isSelectionMode && (
        <div className="bulk-actions" role="toolbar" aria-label="Bulk actions">
          <button
            type="button"
            className="bulk-btn select-all"
            onClick={handleSelectAll}
            aria-label={selectedNotes.length === sortedNotes.length ? 'Deselect all notes' : 'Select all notes'}
          >
            {selectedNotes.length === sortedNotes.length ? 'Deselect All' : 'Select All'}
          </button>
          
          {selectedNotes.length > 0 && (
            <button
              type="button"
              className="bulk-btn delete-selected"
              onClick={handleBulkDelete}
              aria-label={`Delete ${selectedNotes.length} selected note${selectedNotes.length > 1 ? 's' : ''}`}
            >
              Delete Selected ({selectedNotes.length})
            </button>
          )}
        </div>
      )}

      {/* Notes grid */}
      <div 
        className="notes-grid"
        role="list"
        aria-label={`${sortedNotes.length} notes`}
      >
        {sortedNotes.map((note) => (
          <div
            key={note.id}
            role="listitem"
            onMouseEnter={() => setHoveredNoteId(note.id)}
            onMouseLeave={() => setHoveredNoteId(null)}
          >
            <NoteCard
              note={note}
              onEdit={() => onNoteEdit?.(note)}
              onDelete={() => onNoteDelete?.(note.id)}
              onSelect={(isSelected) => handleNoteSelect(note.id, isSelected)}
              isSelected={selectedNotes.includes(note.id)}
              isHovered={hoveredNoteId === note.id}
              showPreview={hoveredNoteId === note.id}
              selectionMode={isSelectionMode}
            />
          </div>
        ))}
      </div>

      {/* Quick stats */}
      <div className="notes-stats" aria-label="Notes statistics">
        <span>Total words: {sortedNotes.reduce((sum, note) => sum + (note.wordCount || 0), 0)}</span>
        <span className="separator">•</span>
        <span>Last updated: {sortedNotes[0] ? new Date(sortedNotes[0].timestamp).toLocaleDateString() : 'Never'}</span>
      </div>
    </div>
  );
};

NotesList.propTypes = {
  notes: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string,
      content: PropTypes.string.isRequired,
      timestamp: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.instanceOf(Date)
      ]).isRequired,
      tags: PropTypes.arrayOf(PropTypes.string),
      wordCount: PropTypes.number,
      relevanceScore: PropTypes.number
    })
  ),
  onNoteEdit: PropTypes.func,
  onNoteDelete: PropTypes.func,
  onNotesSelect: PropTypes.func,
  selectedNotes: PropTypes.arrayOf(PropTypes.string),
  sortBy: PropTypes.oneOf(['date', 'title', 'content', 'relevance']),
  sortOrder: PropTypes.oneOf(['asc', 'desc']),
  onSortChange: PropTypes.func,
  className: PropTypes.string,
  loading: PropTypes.bool,
  emptyMessage: PropTypes.string
};

export default NotesList;