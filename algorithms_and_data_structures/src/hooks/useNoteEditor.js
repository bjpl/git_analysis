/**
 * Note Editor Hook
 * Manages editor state, auto-save, and content operations
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useDebounce } from './useDebounce.js';
import { notesService } from '../services/NotesService.js';

const INITIAL_EDITOR_STATE = {
  note: null,
  originalNote: null,
  isDirty: false,
  isValid: true,
  validationErrors: [],
  lastSaved: null,
  wordCount: 0,
  readingTime: 0,
  cursorPosition: 0,
  selectionRange: { start: 0, end: 0 },
  history: {
    past: [],
    future: []
  }
};

const AUTO_SAVE_DELAY = 2000; // ms
const MAX_HISTORY_SIZE = 50;

export function useNoteEditor(noteId = null, options = {}) {
  const {
    autoSave = true,
    enableHistory = true,
    enableValidation = true,
    onSave = null,
    onError = null,
    onDirtyChange = null
  } = options;

  const [state, setState] = useState(INITIAL_EDITOR_STATE);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  const autoSaveTimeoutRef = useRef(null);
  const editorRef = useRef(null);
  const lastSaveRef = useRef(null);

  // Debounce content changes for auto-save
  const debouncedNote = useDebounce(state.note, AUTO_SAVE_DELAY);

  /**
   * Load a note for editing
   */
  const loadNote = useCallback(async (id) => {
    if (!id) {
      setState(INITIAL_EDITOR_STATE);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const note = await notesService.read(id);
      const editorState = {
        ...INITIAL_EDITOR_STATE,
        note: { ...note },
        originalNote: { ...note },
        wordCount: countWords(note.content || ''),
        readingTime: calculateReadingTime(note.content || ''),
        lastSaved: new Date(note.updatedAt)
      };

      setState(editorState);
    } catch (error) {
      console.error('Failed to load note:', error);
      setError(error.message);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [onError]);

  /**
   * Create a new note for editing
   */
  const createNewNote = useCallback((initialData = {}) => {
    const newNote = {
      id: null, // Will be assigned on first save
      title: initialData.title || '',
      content: initialData.content || '',
      tags: initialData.tags || [],
      category: initialData.category || 'default',
      isPinned: Boolean(initialData.isPinned),
      isArchived: Boolean(initialData.isArchived),
      metadata: initialData.metadata || {}
    };

    setState({
      ...INITIAL_EDITOR_STATE,
      note: newNote,
      originalNote: null,
      wordCount: countWords(newNote.content),
      readingTime: calculateReadingTime(newNote.content)
    });

    setError(null);
  }, []);

  /**
   * Update note content
   */
  const updateNote = useCallback((updates) => {
    setState(prev => {
      if (!prev.note) return prev;

      const updatedNote = { ...prev.note, ...updates };
      const content = updatedNote.content || '';
      
      // Add to history if enabled
      let newHistory = prev.history;
      if (enableHistory && prev.note) {
        newHistory = {
          past: [
            ...prev.history.past.slice(-MAX_HISTORY_SIZE + 1),
            { ...prev.note }
          ],
          future: [] // Clear future when making new changes
        };
      }

      // Calculate derived values
      const wordCount = countWords(content);
      const readingTime = calculateReadingTime(content);

      // Check if dirty
      const isDirty = prev.originalNote ? 
        JSON.stringify(updatedNote) !== JSON.stringify(prev.originalNote) : 
        true;

      // Validate if enabled
      let validationErrors = [];
      let isValid = true;
      
      if (enableValidation) {
        const validation = validateNoteContent(updatedNote);
        validationErrors = validation.errors;
        isValid = validation.isValid;
      }

      const newState = {
        ...prev,
        note: updatedNote,
        isDirty,
        isValid,
        validationErrors,
        wordCount,
        readingTime,
        history: newHistory
      };

      // Notify dirty state change
      if (isDirty !== prev.isDirty) {
        onDirtyChange?.(isDirty);
      }

      return newState;
    });
  }, [enableHistory, enableValidation, onDirtyChange]);

  /**
   * Save the current note
   */
  const saveNote = useCallback(async () => {
    if (!state.note || !state.isDirty || !state.isValid) {
      return false;
    }

    setIsSaving(true);
    setError(null);

    try {
      let savedNote;
      
      if (state.note.id) {
        // Update existing note
        savedNote = await notesService.update(state.note.id, state.note);
      } else {
        // Create new note
        savedNote = await notesService.create(state.note);
      }

      setState(prev => ({
        ...prev,
        note: { ...savedNote },
        originalNote: { ...savedNote },
        isDirty: false,
        lastSaved: new Date()
      }));

      lastSaveRef.current = Date.now();
      onSave?.(savedNote);
      
      return savedNote;
    } catch (error) {
      console.error('Failed to save note:', error);
      setError(error.message);
      onError?.(error);
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [state.note, state.isDirty, state.isValid, onSave, onError]);

  /**
   * Auto-save functionality
   */
  useEffect(() => {
    if (!autoSave || !state.isDirty || !state.isValid || isSaving) {
      return;
    }

    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }

    autoSaveTimeoutRef.current = setTimeout(() => {
      saveNote();
    }, AUTO_SAVE_DELAY);

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [debouncedNote, autoSave, state.isDirty, state.isValid, isSaving, saveNote]);

  /**
   * Undo last change
   */
  const undo = useCallback(() => {
    setState(prev => {
      if (!enableHistory || prev.history.past.length === 0) {
        return prev;
      }

      const previousState = prev.history.past[prev.history.past.length - 1];
      const newPast = prev.history.past.slice(0, -1);
      const newFuture = [prev.note, ...prev.history.future.slice(0, MAX_HISTORY_SIZE - 1)];

      return {
        ...prev,
        note: previousState,
        history: {
          past: newPast,
          future: newFuture
        }
      };
    });
  }, [enableHistory]);

  /**
   * Redo last undone change
   */
  const redo = useCallback(() => {
    setState(prev => {
      if (!enableHistory || prev.history.future.length === 0) {
        return prev;
      }

      const nextState = prev.history.future[0];
      const newFuture = prev.history.future.slice(1);
      const newPast = [...prev.history.past.slice(-MAX_HISTORY_SIZE + 1), prev.note];

      return {
        ...prev,
        note: nextState,
        history: {
          past: newPast,
          future: newFuture
        }
      };
    });
  }, [enableHistory]);

  /**
   * Insert text at cursor position
   */
  const insertText = useCallback((text, cursorOffset = 0) => {
    if (!state.note || !editorRef.current) return;

    const textarea = editorRef.current;
    const { selectionStart, selectionEnd } = textarea;
    const currentContent = state.note.content || '';
    
    const newContent = 
      currentContent.substring(0, selectionStart) + 
      text + 
      currentContent.substring(selectionEnd);

    updateNote({ content: newContent });

    // Set cursor position after insertion
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        selectionStart + text.length + cursorOffset, 
        selectionStart + text.length + cursorOffset
      );
    }, 0);
  }, [state.note, updateNote]);

  /**
   * Replace selected text
   */
  const replaceSelection = useCallback((replacement) => {
    if (!editorRef.current) return;

    const textarea = editorRef.current;
    const { selectionStart, selectionEnd } = textarea;
    
    if (selectionStart === selectionEnd) {
      // No selection, just insert
      insertText(replacement);
    } else {
      // Replace selection
      const currentContent = state.note?.content || '';
      const newContent = 
        currentContent.substring(0, selectionStart) + 
        replacement + 
        currentContent.substring(selectionEnd);

      updateNote({ content: newContent });

      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(
          selectionStart + replacement.length, 
          selectionStart + replacement.length
        );
      }, 0);
    }
  }, [state.note, insertText, updateNote]);

  /**
   * Get selected text
   */
  const getSelectedText = useCallback(() => {
    if (!editorRef.current || !state.note) return '';

    const { selectionStart, selectionEnd } = editorRef.current;
    return state.note.content?.substring(selectionStart, selectionEnd) || '';
  }, [state.note]);

  /**
   * Reset editor state
   */
  const reset = useCallback(() => {
    setState(INITIAL_EDITOR_STATE);
    setError(null);
    setIsLoading(false);
    setIsSaving(false);

    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
  }, []);

  /**
   * Discard changes and revert to original
   */
  const discardChanges = useCallback(() => {
    if (!state.originalNote) return;

    setState(prev => ({
      ...prev,
      note: { ...prev.originalNote },
      isDirty: false,
      history: { past: [], future: [] }
    }));
  }, [state.originalNote]);

  // Load note when noteId changes
  useEffect(() => {
    if (noteId) {
      loadNote(noteId);
    } else {
      reset();
    }
  }, [noteId, loadNote, reset]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, []);

  return {
    // State
    note: state.note,
    originalNote: state.originalNote,
    isDirty: state.isDirty,
    isValid: state.isValid,
    validationErrors: state.validationErrors,
    lastSaved: state.lastSaved,
    wordCount: state.wordCount,
    readingTime: state.readingTime,
    isLoading,
    isSaving,
    error,

    // History
    canUndo: enableHistory && state.history.past.length > 0,
    canRedo: enableHistory && state.history.future.length > 0,

    // Actions
    loadNote,
    createNewNote,
    updateNote,
    saveNote,
    undo,
    redo,
    insertText,
    replaceSelection,
    getSelectedText,
    reset,
    discardChanges,

    // Editor ref
    editorRef,

    // Status
    hasUnsavedChanges: state.isDirty && state.isValid,
    isReadyToSave: state.isDirty && state.isValid && !isSaving
  };
}

// Helper functions
function countWords(text) {
  return text.trim().split(/\s+/).filter(word => word.length > 0).length;
}

function calculateReadingTime(text) {
  const wordsPerMinute = 200;
  const wordCount = countWords(text);
  return Math.ceil(wordCount / wordsPerMinute);
}

function validateNoteContent(note) {
  const errors = [];

  if (!note.title || note.title.trim().length === 0) {
    errors.push('Title is required');
  }

  if (note.title && note.title.length > 200) {
    errors.push('Title must be less than 200 characters');
  }

  if (note.content && note.content.length > 1000000) {
    errors.push('Content must be less than 1MB');
  }

  if (note.tags && note.tags.length > 20) {
    errors.push('Maximum 20 tags allowed');
  }

  if (note.category && note.category.length > 50) {
    errors.push('Category must be less than 50 characters');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}