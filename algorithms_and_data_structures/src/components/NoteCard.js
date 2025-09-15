import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { formatTimestamp, truncateText } from '../utils/helpers';
import './NoteCard.css';

const NoteCard = ({
  note,
  onEdit,
  onDelete,
  onSelect,
  isSelected = false,
  isHovered = false,
  showPreview = false,
  selectionMode = false,
  maxPreviewLength = 150,
  className = ''
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const menuRef = useRef(null);
  const cardRef = useRef(null);

  // Extract title from content (first line or first sentence)
  const getTitle = () => {
    if (note.title) return note.title;
    
    const firstLine = note.content.split('\n')[0].trim();
    if (firstLine.startsWith('#')) {
      return firstLine.replace(/^#+\s*/, '');
    }
    
    const firstSentence = note.content.split('.')[0].trim();
    return truncateText(firstSentence, 50) || 'Untitled Note';
  };

  // Get preview content (exclude title)
  const getPreviewContent = () => {
    const lines = note.content.split('\n').filter(line => line.trim());
    const contentWithoutTitle = lines.slice(lines[0].startsWith('#') ? 1 : 0).join(' ');
    return truncateText(contentWithoutTitle, maxPreviewLength);
  };

  // Get context information (lesson, timestamp, etc.)
  const getContextInfo = () => {
    const info = [];
    
    if (note.lessonId) {
      info.push(`Lesson: ${note.lessonId}`);
    }
    
    if (note.wordCount) {
      info.push(`${note.wordCount} words`);
    }
    
    return info.join(' • ');
  };

  // Handle card click
  const handleCardClick = (e) => {
    e.preventDefault();
    
    if (selectionMode) {
      onSelect?.(!isSelected);
    } else {
      onEdit?.();
    }
  };

  // Handle selection change
  const handleSelectionChange = (e) => {
    e.stopPropagation();
    onSelect?.(!isSelected);
  };

  // Handle menu toggle
  const handleMenuToggle = (e) => {
    e.stopPropagation();
    setIsMenuOpen(!isMenuOpen);
  };

  // Handle delete
  const handleDelete = (e) => {
    e.stopPropagation();
    if (showDeleteConfirm) {
      onDelete?.();
      setShowDeleteConfirm(false);
      setIsMenuOpen(false);
    } else {
      setShowDeleteConfirm(true);
    }
  };

  // Handle edit
  const handleEdit = (e) => {
    e.stopPropagation();
    onEdit?.();
    setIsMenuOpen(false);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        handleCardClick(e);
        break;
      case 'Delete':
      case 'Backspace':
        if (e.shiftKey) {
          e.preventDefault();
          onDelete?.();
        }
        break;
      case 'Escape':
        setIsMenuOpen(false);
        setShowDeleteConfirm(false);
        break;
      default:
        break;
    }
  };

  // Close menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsMenuOpen(false);
        setShowDeleteConfirm(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isMenuOpen]);

  const title = getTitle();
  const preview = getPreviewContent();
  const contextInfo = getContextInfo();
  const timestamp = formatTimestamp(note.timestamp);

  return (
    <article
      ref={cardRef}
      className={`note-card ${className} ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''} ${selectionMode ? 'selection-mode' : ''}`}
      onClick={handleCardClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`Note: ${title}`}
      aria-pressed={selectionMode ? isSelected : undefined}
      aria-describedby={`note-${note.id}-preview note-${note.id}-meta`}
    >
      {/* Selection checkbox */}
      {selectionMode && (
        <div className="note-card__selection">
          <input
            type="checkbox"
            className="selection-checkbox"
            checked={isSelected}
            onChange={handleSelectionChange}
            aria-label={`Select note: ${title}`}
            tabIndex={-1}
          />
        </div>
      )}

      {/* Main content */}
      <div className="note-card__content">
        {/* Header */}
        <div className="note-card__header">
          <h3 className="note-title" title={title}>
            {title}
          </h3>
          
          {!selectionMode && (
            <div className="note-card__menu" ref={menuRef}>
              <button
                type="button"
                className="menu-trigger"
                onClick={handleMenuToggle}
                aria-label="Note options"
                aria-expanded={isMenuOpen}
                aria-haspopup="menu"
              >
                ⋮
              </button>
              
              {isMenuOpen && (
                <div className="menu-dropdown" role="menu">
                  <button
                    type="button"
                    className="menu-item edit"
                    onClick={handleEdit}
                    role="menuitem"
                  >
                    ✏ Edit
                  </button>
                  <button
                    type="button"
                    className={`menu-item delete ${showDeleteConfirm ? 'confirm' : ''}`}
                    onClick={handleDelete}
                    role="menuitem"
                    aria-label={showDeleteConfirm ? 'Confirm delete' : 'Delete note'}
                  >
                    {showDeleteConfirm ? '✓ Confirm' : '🗑 Delete'}
                  </button>
                  {showDeleteConfirm && (
                    <button
                      type="button"
                      className="menu-item cancel"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowDeleteConfirm(false);
                      }}
                      role="menuitem"
                    >
                      ✕ Cancel
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Preview content */}
        {preview && (
          <div 
            id={`note-${note.id}-preview`}
            className="note-preview"
            title={showPreview ? note.content : undefined}
          >
            {preview}
            {note.content.length > maxPreviewLength && (
              <span className="preview-more">...</span>
            )}
          </div>
        )}

        {/* Extended preview on hover */}
        {showPreview && isHovered && note.content.length > maxPreviewLength && (
          <div className="note-extended-preview">
            <div className="extended-preview-content">
              {note.content}
            </div>
          </div>
        )}

        {/* Tags */}
        {note.tags && note.tags.length > 0 && (
          <div className="note-tags" aria-label="Note tags">
            {note.tags.map(tag => (
              <span key={tag} className="tag">
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Footer with metadata */}
      <div id={`note-${note.id}-meta`} className="note-card__footer">
        <div className="note-timestamp" title={`Created: ${timestamp.full}`}>
          <time dateTime={note.timestamp}>
            {timestamp.relative}
          </time>
        </div>
        
        {contextInfo && (
          <div className="note-context" title={contextInfo}>
            {contextInfo}
          </div>
        )}
        
        {/* Status indicators */}
        <div className="note-indicators">
          {note.isBookmarked && (
            <span className="indicator bookmark" aria-label="Bookmarked" title="Bookmarked">
              ★
            </span>
          )}
          {note.hasReminder && (
            <span className="indicator reminder" aria-label="Has reminder" title="Has reminder">
              🔔
            </span>
          )}
          {note.isShared && (
            <span className="indicator shared" aria-label="Shared" title="Shared">
              🔗
            </span>
          )}
        </div>
      </div>
    </article>
  );
};

NoteCard.propTypes = {
  note: PropTypes.shape({
    id: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    title: PropTypes.string,
    timestamp: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.instanceOf(Date)
    ]).isRequired,
    tags: PropTypes.arrayOf(PropTypes.string),
    lessonId: PropTypes.string,
    wordCount: PropTypes.number,
    isBookmarked: PropTypes.bool,
    hasReminder: PropTypes.bool,
    isShared: PropTypes.bool
  }).isRequired,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  onSelect: PropTypes.func,
  isSelected: PropTypes.bool,
  isHovered: PropTypes.bool,
  showPreview: PropTypes.bool,
  selectionMode: PropTypes.bool,
  maxPreviewLength: PropTypes.number,
  className: PropTypes.string
};

export default NoteCard;