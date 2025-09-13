import React, { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { debounce } from '../utils/helpers';
import './NoteEditor.css';

const NoteEditor = ({
  note,
  onSave,
  onCancel,
  autoSave = true,
  placeholder = "Start writing your notes...",
  maxLength = 10000,
  className = "",
  disabled = false
}) => {
  const [content, setContent] = useState(note?.content || '');
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const textareaRef = useRef(null);
  const saveTimeoutRef = useRef(null);

  // Calculate word and character counts
  const updateCounts = useCallback((text) => {
    const words = text.trim().split(/\s+/).filter(word => word.length > 0).length;
    const chars = text.length;
    setWordCount(words);
    setCharCount(chars);
  }, []);

  // Debounced auto-save function
  const debouncedSave = useCallback(
    debounce(async (text) => {
      if (autoSave && text.trim() && onSave) {
        setIsSaving(true);
        try {
          await onSave(text);
          setLastSaved(new Date());
        } catch (error) {
          console.error('Auto-save failed:', error);
        } finally {
          setIsSaving(false);
        }
      }
    }, 1500),
    [autoSave, onSave]
  );

  // Handle content changes
  const handleContentChange = (e) => {
    const newContent = e.target.value;
    if (newContent.length <= maxLength) {
      setContent(newContent);
      updateCounts(newContent);
      
      if (autoSave) {
        debouncedSave(newContent);
      }
    }
  };

  // Initialize counts on mount
  useEffect(() => {
    updateCounts(content);
  }, [content, updateCounts]);

  // Format text functions
  const applyFormatting = (format) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);
    const beforeText = content.substring(0, start);
    const afterText = content.substring(end);

    let formattedText;
    switch (format) {
      case 'bold':
        formattedText = `**${selectedText}**`;
        setIsBold(!isBold);
        break;
      case 'italic':
        formattedText = `*${selectedText}*`;
        setIsItalic(!isItalic);
        break;
      case 'heading':
        formattedText = `\n## ${selectedText}`;
        break;
      case 'bullet':
        formattedText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
        break;
      default:
        formattedText = selectedText;
    }

    const newContent = beforeText + formattedText + afterText;
    if (newContent.length <= maxLength) {
      setContent(newContent);
      updateCounts(newContent);
      
      // Focus and set cursor position
      setTimeout(() => {
        textarea.focus();
        const newCursorPos = start + formattedText.length;
        textarea.setSelectionRange(newCursorPos, newCursorPos);
      }, 0);
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'b':
          e.preventDefault();
          applyFormatting('bold');
          break;
        case 'i':
          e.preventDefault();
          applyFormatting('italic');
          break;
        case 's':
          e.preventDefault();
          if (onSave && content.trim()) {
            onSave(content);
          }
          break;
        default:
          break;
      }
    }
  };

  // Manual save
  const handleSave = async () => {
    if (onSave && content.trim()) {
      setIsSaving(true);
      try {
        await onSave(content);
        setLastSaved(new Date());
      } catch (error) {
        console.error('Save failed:', error);
      } finally {
        setIsSaving(false);
      }
    }
  };

  // Format last saved time
  const formatLastSaved = (date) => {
    if (!date) return '';
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Saved just now';
    if (minutes < 60) return `Saved ${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return `Saved at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  return (
    <div className={`note-editor ${className}`} role="region" aria-label="Note editor">
      {/* Formatting Toolbar */}
      <div className="note-editor__toolbar" role="toolbar" aria-label="Text formatting">
        <button
          type="button"
          className={`toolbar-btn ${isBold ? 'active' : ''}`}
          onClick={() => applyFormatting('bold')}
          disabled={disabled}
          aria-label="Bold text"
          title="Bold (Ctrl+B)"
        >
          <strong>B</strong>
        </button>
        <button
          type="button"
          className={`toolbar-btn ${isItalic ? 'active' : ''}`}
          onClick={() => applyFormatting('italic')}
          disabled={disabled}
          aria-label="Italic text"
          title="Italic (Ctrl+I)"
        >
          <em>I</em>
        </button>
        <button
          type="button"
          className="toolbar-btn"
          onClick={() => applyFormatting('heading')}
          disabled={disabled}
          aria-label="Heading"
          title="Add heading"
        >
          H
        </button>
        <button
          type="button"
          className="toolbar-btn"
          onClick={() => applyFormatting('bullet')}
          disabled={disabled}
          aria-label="Bullet list"
          title="Add bullet points"
        >
          •
        </button>
        
        <div className="toolbar-divider" />
        
        <button
          type="button"
          className="toolbar-btn save-btn"
          onClick={handleSave}
          disabled={disabled || isSaving || !content.trim()}
          aria-label="Save note"
          title="Save (Ctrl+S)"
        >
          {isSaving ? '⏳' : '💾'}
        </button>
        
        {onCancel && (
          <button
            type="button"
            className="toolbar-btn cancel-btn"
            onClick={onCancel}
            disabled={disabled}
            aria-label="Cancel editing"
            title="Cancel"
          >
            ✕
          </button>
        )}
      </div>

      {/* Main Editor */}
      <div className="note-editor__main">
        <textarea
          ref={textareaRef}
          className="note-editor__textarea"
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          aria-label="Note content"
          aria-describedby="note-stats note-save-status"
          rows="20"
          autoFocus
        />
      </div>

      {/* Status Bar */}
      <div className="note-editor__status">
        <div id="note-stats" className="status-counts">
          <span aria-label={`${wordCount} words`}>
            {wordCount} word{wordCount !== 1 ? 's' : ''}
          </span>
          <span className="separator">•</span>
          <span aria-label={`${charCount} of ${maxLength} characters`}>
            {charCount}/{maxLength}
          </span>
        </div>
        
        <div id="note-save-status" className="status-save">
          {isSaving && (
            <span className="saving-indicator" aria-live="polite">
              Saving...
            </span>
          )}
          {lastSaved && !isSaving && (
            <span className="saved-indicator" aria-live="polite">
              {formatLastSaved(lastSaved)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

NoteEditor.propTypes = {
  note: PropTypes.shape({
    id: PropTypes.string,
    content: PropTypes.string,
    timestamp: PropTypes.instanceOf(Date)
  }),
  onSave: PropTypes.func.isRequired,
  onCancel: PropTypes.func,
  autoSave: PropTypes.bool,
  placeholder: PropTypes.string,
  maxLength: PropTypes.number,
  className: PropTypes.string,
  disabled: PropTypes.bool
};

export default NoteEditor;