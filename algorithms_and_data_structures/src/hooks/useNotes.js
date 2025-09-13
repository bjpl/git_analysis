/**
 * Main notes state management hook
 * Provides comprehensive notes management with optimistic updates
 */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { notesService } from '../services/NotesService.js';
import { useDebounce } from './useDebounce.js';

const INITIAL_STATE = {
  notes: [],
  loading: false,
  error: null,
  filter: {
    search: '',
    category: '',
    tags: [],
    isPinned: undefined,
    isArchived: false,
    sortBy: 'updatedAt',
    sortOrder: 'desc'
  },
  pagination: {
    offset: 0,
    limit: 50,
    hasMore: true
  }
};

export function useNotes(options = {}) {
  const [state, setState] = useState(INITIAL_STATE);
  const [statistics, setStatistics] = useState(null);
  const unsubscribeRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Debounce search to avoid excessive API calls
  const debouncedSearch = useDebounce(state.filter.search, 300);

  /**
   * Initialize notes service and load data
   */
  const initialize = useCallback(async () => {
    if (state.loading) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Cancel any ongoing operations
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      await notesService.initialize();
      await loadNotes();
      await loadStatistics();

      // Subscribe to service events
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      unsubscribeRef.current = notesService.subscribe(handleServiceEvent);

    } catch (error) {
      console.error('Failed to initialize notes:', error);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error.message || 'Failed to initialize notes' 
      }));
    }
  }, [state.loading]);

  /**
   * Load notes with current filter and pagination
   */
  const loadNotes = useCallback(async (resetPagination = false) => {
    try {
      if (resetPagination) {
        setState(prev => ({ 
          ...prev, 
          pagination: { ...prev.pagination, offset: 0, hasMore: true } 
        }));
      }

      const filterOptions = {
        ...state.filter,
        search: debouncedSearch,
        offset: resetPagination ? 0 : state.pagination.offset,
        limit: state.pagination.limit + 1 // Load one extra to check if there are more
      };

      const loadedNotes = await notesService.list(filterOptions);
      
      const hasMore = loadedNotes.length > state.pagination.limit;
      const notes = hasMore ? loadedNotes.slice(0, -1) : loadedNotes;

      setState(prev => ({
        ...prev,
        notes: resetPagination ? notes : [...prev.notes, ...notes],
        loading: false,
        error: null,
        pagination: {
          ...prev.pagination,
          hasMore,
          offset: resetPagination ? notes.length : prev.pagination.offset + notes.length
        }
      }));

    } catch (error) {
      console.error('Failed to load notes:', error);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error.message || 'Failed to load notes' 
      }));
    }
  }, [state.filter, state.pagination.offset, state.pagination.limit, debouncedSearch]);

  /**
   * Load notes statistics
   */
  const loadStatistics = useCallback(async () => {
    try {
      const stats = await notesService.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  }, []);

  /**
   * Handle service events (optimistic updates)
   */
  const handleServiceEvent = useCallback((event) => {
    switch (event.type) {
      case 'NOTE_CREATED':
        setState(prev => ({
          ...prev,
          notes: [event.payload, ...prev.notes]
        }));
        loadStatistics();
        break;

      case 'NOTE_UPDATED':
        setState(prev => ({
          ...prev,
          notes: prev.notes.map(note => 
            note.id === event.payload.id ? event.payload : note
          )
        }));
        break;

      case 'NOTE_DELETED':
        setState(prev => ({
          ...prev,
          notes: prev.notes.filter(note => note.id !== event.payload.id)
        }));
        loadStatistics();
        break;

      case 'NOTES_LOADED':
        setState(prev => ({
          ...prev,
          notes: event.payload,
          loading: false
        }));
        break;

      case 'NOTES_IMPORTED':
        loadNotes(true);
        loadStatistics();
        break;

      default:
        console.warn('Unknown service event:', event.type);
    }
  }, [loadNotes, loadStatistics]);

  /**
   * Create a new note
   */
  const createNote = useCallback(async (noteData) => {
    try {
      const newNote = await notesService.create(noteData);
      return newNote;
    } catch (error) {
      console.error('Failed to create note:', error);
      setState(prev => ({ ...prev, error: error.message }));
      throw error;
    }
  }, []);

  /**
   * Update an existing note
   */
  const updateNote = useCallback(async (id, updateData) => {
    try {
      const updatedNote = await notesService.update(id, updateData);
      return updatedNote;
    } catch (error) {
      console.error('Failed to update note:', error);
      setState(prev => ({ ...prev, error: error.message }));
      
      // Revert optimistic update on error
      loadNotes(true);
      throw error;
    }
  }, [loadNotes]);

  /**
   * Delete a note
   */
  const deleteNote = useCallback(async (id) => {
    try {
      await notesService.delete(id);
      return true;
    } catch (error) {
      console.error('Failed to delete note:', error);
      setState(prev => ({ ...prev, error: error.message }));
      
      // Revert optimistic update on error
      loadNotes(true);
      throw error;
    }
  }, [loadNotes]);

  /**
   * Batch operations
   */
  const batchDelete = useCallback(async (noteIds) => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      const result = await notesService.batchOperation('delete', noteIds);
      await loadNotes(true);
      await loadStatistics();
      return result;
    } catch (error) {
      console.error('Failed to batch delete notes:', error);
      setState(prev => ({ ...prev, error: error.message }));
      throw error;
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, [loadNotes, loadStatistics]);

  /**
   * Update filters
   */
  const updateFilter = useCallback((filterUpdate) => {
    setState(prev => ({
      ...prev,
      filter: { ...prev.filter, ...filterUpdate },
      pagination: { ...prev.pagination, offset: 0, hasMore: true }
    }));
  }, []);

  /**
   * Reset filters
   */
  const resetFilter = useCallback(() => {
    setState(prev => ({
      ...prev,
      filter: INITIAL_STATE.filter,
      pagination: INITIAL_STATE.pagination
    }));
  }, []);

  /**
   * Load more notes (pagination)
   */
  const loadMore = useCallback(async () => {
    if (!state.pagination.hasMore || state.loading) return;

    setState(prev => ({ ...prev, loading: true }));
    await loadNotes(false);
  }, [state.pagination.hasMore, state.loading, loadNotes]);

  /**
   * Refresh notes
   */
  const refresh = useCallback(async () => {
    await loadNotes(true);
    await loadStatistics();
  }, [loadNotes, loadStatistics]);

  /**
   * Search notes
   */
  const searchNotes = useCallback(async (query, searchOptions = {}) => {
    try {
      const results = await notesService.search(query, searchOptions);
      return results;
    } catch (error) {
      console.error('Search failed:', error);
      throw error;
    }
  }, []);

  /**
   * Export notes
   */
  const exportNotes = useCallback(async (format = 'json', exportOptions = {}) => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      const data = await notesService.export(format, exportOptions);
      return data;
    } catch (error) {
      console.error('Export failed:', error);
      setState(prev => ({ ...prev, error: error.message }));
      throw error;
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, []);

  /**
   * Import notes
   */
  const importNotes = useCallback(async (data, format = 'json', importOptions = {}) => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      const result = await notesService.import(data, format, importOptions);
      await refresh();
      return result;
    } catch (error) {
      console.error('Import failed:', error);
      setState(prev => ({ ...prev, error: error.message }));
      throw error;
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, [refresh]);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Effect to load notes when filter changes
  useEffect(() => {
    if (debouncedSearch !== state.filter.search || 
        Object.keys(options).some(key => options[key] !== state.filter[key])) {
      loadNotes(true);
    }
  }, [debouncedSearch, state.filter, options, loadNotes]);

  // Effect to initialize on mount
  useEffect(() => {
    initialize();

    // Cleanup on unmount
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [initialize]);

  // Computed values
  const filteredNotesCount = useMemo(() => state.notes.length, [state.notes.length]);
  
  const selectedCategories = useMemo(() => {
    const categories = new Set();
    state.notes.forEach(note => {
      if (note.category) categories.add(note.category);
    });
    return Array.from(categories);
  }, [state.notes]);

  const selectedTags = useMemo(() => {
    const tags = new Set();
    state.notes.forEach(note => {
      note.tags.forEach(tag => tags.add(tag));
    });
    return Array.from(tags);
  }, [state.notes]);

  return {
    // State
    notes: state.notes,
    loading: state.loading,
    error: state.error,
    filter: state.filter,
    pagination: state.pagination,
    statistics,
    filteredNotesCount,
    selectedCategories,
    selectedTags,

    // Actions
    createNote,
    updateNote,
    deleteNote,
    batchDelete,
    updateFilter,
    resetFilter,
    loadMore,
    refresh,
    searchNotes,
    exportNotes,
    importNotes,
    clearError,

    // Status
    hasMore: state.pagination.hasMore,
    isEmpty: state.notes.length === 0 && !state.loading,
    isInitialized: !state.loading && !state.error
  };
}