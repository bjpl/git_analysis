/**
 * Notes State Management (Redux-style slice)
 * Central state management for notes with actions and selectors
 */

import { createSlice, createAsyncThunk, createSelector } from '@reduxjs/toolkit';
import { notesService } from '../services/NotesService.js';

// Async thunks for API operations
export const initializeNotes = createAsyncThunk(
  'notes/initialize',
  async (_, { rejectWithValue }) => {
    try {
      await notesService.initialize();
      const notes = await notesService.list();
      const statistics = await notesService.getStatistics();
      return { notes, statistics };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const createNote = createAsyncThunk(
  'notes/create',
  async (noteData, { rejectWithValue }) => {
    try {
      const note = await notesService.create(noteData);
      return note;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateNote = createAsyncThunk(
  'notes/update',
  async ({ id, data }, { rejectWithValue, getState }) => {
    try {
      const note = await notesService.update(id, data);
      return note;
    } catch (error) {
      // Revert optimistic update on error
      return rejectWithValue({ error: error.message, id });
    }
  }
);

export const deleteNote = createAsyncThunk(
  'notes/delete',
  async (id, { rejectWithValue }) => {
    try {
      await notesService.delete(id);
      return id;
    } catch (error) {
      return rejectWithValue({ error: error.message, id });
    }
  }
);

export const batchDeleteNotes = createAsyncThunk(
  'notes/batchDelete',
  async (noteIds, { rejectWithValue }) => {
    try {
      const result = await notesService.batchOperation('delete', noteIds);
      return { noteIds, result };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const searchNotes = createAsyncThunk(
  'notes/search',
  async ({ query, options }, { rejectWithValue }) => {
    try {
      const results = await notesService.search(query, options);
      return { query, results, options };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const loadMoreNotes = createAsyncThunk(
  'notes/loadMore',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState().notes;
      const options = {
        ...state.filters,
        offset: state.notes.length,
        limit: state.pagination.limit
      };
      const notes = await notesService.list(options);
      return notes;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const exportNotes = createAsyncThunk(
  'notes/export',
  async ({ format, options }, { rejectWithValue }) => {
    try {
      const data = await notesService.export(format, options);
      return { format, data };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const importNotes = createAsyncThunk(
  'notes/import',
  async ({ data, format, options }, { rejectWithValue }) => {
    try {
      const result = await notesService.import(data, format, options);
      return result;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Initial state
const initialState = {
  // Data
  notes: [],
  statistics: null,
  searchResults: [],
  
  // UI state
  selectedNoteIds: [],
  currentNoteId: null,
  
  // Filters and sorting
  filters: {
    search: '',
    category: '',
    tags: [],
    isPinned: undefined,
    isArchived: false,
    dateRange: null
  },
  
  sort: {
    field: 'updatedAt',
    order: 'desc'
  },
  
  // Pagination
  pagination: {
    limit: 50,
    hasMore: true,
    total: 0
  },
  
  // View state
  view: {
    mode: 'list', // 'list', 'grid', 'cards'
    sidebarOpen: true,
    editorOpen: false,
    searchOpen: false
  },
  
  // Operation states
  loading: {
    notes: false,
    search: false,
    create: false,
    update: {},
    delete: {},
    export: false,
    import: false
  },
  
  // Error handling
  errors: {
    notes: null,
    search: null,
    create: null,
    update: {},
    delete: {},
    export: null,
    import: null
  },
  
  // Cache and metadata
  lastUpdated: null,
  version: '1.0.0'
};

// Create the slice
const notesSlice = createSlice({
  name: 'notes',
  initialState,
  reducers: {
    // UI actions
    selectNote: (state, action) => {
      state.currentNoteId = action.payload;
    },
    
    toggleNoteSelection: (state, action) => {
      const noteId = action.payload;
      const index = state.selectedNoteIds.indexOf(noteId);
      if (index >= 0) {
        state.selectedNoteIds.splice(index, 1);
      } else {
        state.selectedNoteIds.push(noteId);
      }
    },
    
    selectAllNotes: (state) => {
      state.selectedNoteIds = state.notes.map(note => note.id);
    },
    
    clearSelection: (state) => {
      state.selectedNoteIds = [];
    },
    
    // Filter actions
    updateFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
      state.pagination.hasMore = true; // Reset pagination
    },
    
    clearFilters: (state) => {
      state.filters = initialState.filters;
      state.pagination.hasMore = true;
    },
    
    updateSort: (state, action) => {
      state.sort = { ...state.sort, ...action.payload };
    },
    
    // View actions
    updateView: (state, action) => {
      state.view = { ...state.view, ...action.payload };
    },
    
    toggleSidebar: (state) => {
      state.view.sidebarOpen = !state.view.sidebarOpen;
    },
    
    toggleEditor: (state) => {
      state.view.editorOpen = !state.view.editorOpen;
    },
    
    toggleSearch: (state) => {
      state.view.searchOpen = !state.view.searchOpen;
    },
    
    // Error handling
    clearError: (state, action) => {
      const { type, id } = action.payload || {};
      if (type && id) {
        if (state.errors[type]) {
          delete state.errors[type][id];
        }
      } else if (type) {
        state.errors[type] = null;
      } else {
        // Clear all errors
        Object.keys(state.errors).forEach(key => {
          if (typeof state.errors[key] === 'object') {
            state.errors[key] = {};
          } else {
            state.errors[key] = null;
          }
        });
      }
    },
    
    // Optimistic updates
    optimisticUpdateNote: (state, action) => {
      const { id, data } = action.payload;
      const noteIndex = state.notes.findIndex(note => note.id === id);
      if (noteIndex >= 0) {
        state.notes[noteIndex] = { ...state.notes[noteIndex], ...data };
      }
    },
    
    revertOptimisticUpdate: (state, action) => {
      const { id, originalNote } = action.payload;
      const noteIndex = state.notes.findIndex(note => note.id === id);
      if (noteIndex >= 0 && originalNote) {
        state.notes[noteIndex] = originalNote;
      }
    },
    
    // Real-time updates from service
    handleServiceEvent: (state, action) => {
      const { type, payload } = action.payload;
      
      switch (type) {
        case 'NOTE_CREATED':
          state.notes.unshift(payload);
          break;
          
        case 'NOTE_UPDATED':
          const updateIndex = state.notes.findIndex(note => note.id === payload.id);
          if (updateIndex >= 0) {
            state.notes[updateIndex] = payload;
          }
          break;
          
        case 'NOTE_DELETED':
          state.notes = state.notes.filter(note => note.id !== payload.id);
          state.selectedNoteIds = state.selectedNoteIds.filter(id => id !== payload.id);
          if (state.currentNoteId === payload.id) {
            state.currentNoteId = null;
          }
          break;
          
        case 'NOTES_IMPORTED':
          // Refresh notes after import
          break;
          
        default:
          console.warn('Unknown service event:', type);
      }
      
      state.lastUpdated = new Date().toISOString();
    }
  },
  
  extraReducers: (builder) => {
    builder
      // Initialize notes
      .addCase(initializeNotes.pending, (state) => {
        state.loading.notes = true;
        state.errors.notes = null;
      })
      .addCase(initializeNotes.fulfilled, (state, action) => {
        state.loading.notes = false;
        state.notes = action.payload.notes;
        state.statistics = action.payload.statistics;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(initializeNotes.rejected, (state, action) => {
        state.loading.notes = false;
        state.errors.notes = action.payload;
      })
      
      // Create note
      .addCase(createNote.pending, (state) => {
        state.loading.create = true;
        state.errors.create = null;
      })
      .addCase(createNote.fulfilled, (state, action) => {
        state.loading.create = false;
        state.notes.unshift(action.payload);
        state.currentNoteId = action.payload.id;
      })
      .addCase(createNote.rejected, (state, action) => {
        state.loading.create = false;
        state.errors.create = action.payload;
      })
      
      // Update note
      .addCase(updateNote.pending, (state, action) => {
        const { id } = action.meta.arg;
        state.loading.update[id] = true;
        delete state.errors.update[id];
        
        // Optimistic update
        const noteIndex = state.notes.findIndex(note => note.id === id);
        if (noteIndex >= 0) {
          const originalNote = { ...state.notes[noteIndex] };
          state.notes[noteIndex] = { ...originalNote, ...action.meta.arg.data };
          // Store original for potential revert
          state.notes[noteIndex]._originalNote = originalNote;
        }
      })
      .addCase(updateNote.fulfilled, (state, action) => {
        const id = action.payload.id;
        state.loading.update[id] = false;
        
        const noteIndex = state.notes.findIndex(note => note.id === id);
        if (noteIndex >= 0) {
          state.notes[noteIndex] = action.payload;
          delete state.notes[noteIndex]._originalNote;
        }
      })
      .addCase(updateNote.rejected, (state, action) => {
        const { id } = action.payload;
        state.loading.update[id] = false;
        state.errors.update[id] = action.payload.error;
        
        // Revert optimistic update
        const noteIndex = state.notes.findIndex(note => note.id === id);
        if (noteIndex >= 0 && state.notes[noteIndex]._originalNote) {
          state.notes[noteIndex] = state.notes[noteIndex]._originalNote;
        }
      })
      
      // Delete note
      .addCase(deleteNote.pending, (state, action) => {
        const id = action.meta.arg;
        state.loading.delete[id] = true;
        delete state.errors.delete[id];
        
        // Optimistic removal
        const noteIndex = state.notes.findIndex(note => note.id === id);
        if (noteIndex >= 0) {
          state.notes[noteIndex]._isDeleting = true;
        }
      })
      .addCase(deleteNote.fulfilled, (state, action) => {
        const id = action.payload;
        delete state.loading.delete[id];
        
        state.notes = state.notes.filter(note => note.id !== id);
        state.selectedNoteIds = state.selectedNoteIds.filter(noteId => noteId !== id);
        
        if (state.currentNoteId === id) {
          state.currentNoteId = null;
        }
      })
      .addCase(deleteNote.rejected, (state, action) => {
        const { id, error } = action.payload;
        delete state.loading.delete[id];
        state.errors.delete[id] = error;
        
        // Revert optimistic removal
        const noteIndex = state.notes.findIndex(note => note.id === id);
        if (noteIndex >= 0) {
          delete state.notes[noteIndex]._isDeleting;
        }
      })
      
      // Batch delete
      .addCase(batchDeleteNotes.pending, (state, action) => {
        const noteIds = action.meta.arg;
        noteIds.forEach(id => {
          state.loading.delete[id] = true;
          delete state.errors.delete[id];
        });
      })
      .addCase(batchDeleteNotes.fulfilled, (state, action) => {
        const { noteIds, result } = action.payload;
        
        noteIds.forEach(id => {
          delete state.loading.delete[id];
        });
        
        // Remove successfully deleted notes
        const successfulDeletes = result.results
          .filter(r => r.success)
          .map(r => r.item);
        
        state.notes = state.notes.filter(note => 
          !successfulDeletes.includes(note.id)
        );
        
        state.selectedNoteIds = state.selectedNoteIds.filter(id => 
          !successfulDeletes.includes(id)
        );
      })
      .addCase(batchDeleteNotes.rejected, (state, action) => {
        const noteIds = action.meta.arg;
        noteIds.forEach(id => {
          delete state.loading.delete[id];
          state.errors.delete[id] = action.payload;
        });
      })
      
      // Search
      .addCase(searchNotes.pending, (state) => {
        state.loading.search = true;
        state.errors.search = null;
      })
      .addCase(searchNotes.fulfilled, (state, action) => {
        state.loading.search = false;
        state.searchResults = action.payload.results;
        state.filters.search = action.payload.query;
      })
      .addCase(searchNotes.rejected, (state, action) => {
        state.loading.search = false;
        state.errors.search = action.payload;
      })
      
      // Load more
      .addCase(loadMoreNotes.fulfilled, (state, action) => {
        const newNotes = action.payload;
        state.notes.push(...newNotes);
        state.pagination.hasMore = newNotes.length === state.pagination.limit;
      })
      
      // Export
      .addCase(exportNotes.pending, (state) => {
        state.loading.export = true;
        state.errors.export = null;
      })
      .addCase(exportNotes.fulfilled, (state) => {
        state.loading.export = false;
      })
      .addCase(exportNotes.rejected, (state, action) => {
        state.loading.export = false;
        state.errors.export = action.payload;
      })
      
      // Import
      .addCase(importNotes.pending, (state) => {
        state.loading.import = true;
        state.errors.import = null;
      })
      .addCase(importNotes.fulfilled, (state, action) => {
        state.loading.import = false;
        // Note: actual notes will be updated via service events
      })
      .addCase(importNotes.rejected, (state, action) => {
        state.loading.import = false;
        state.errors.import = action.payload;
      });
  }
});

// Export actions
export const {
  selectNote,
  toggleNoteSelection,
  selectAllNotes,
  clearSelection,
  updateFilters,
  clearFilters,
  updateSort,
  updateView,
  toggleSidebar,
  toggleEditor,
  toggleSearch,
  clearError,
  optimisticUpdateNote,
  revertOptimisticUpdate,
  handleServiceEvent
} = notesSlice.actions;

// Selectors
export const selectAllNotes = (state) => state.notes.notes;
export const selectCurrentNote = (state) => {
  const currentId = state.notes.currentNoteId;
  return currentId ? state.notes.notes.find(note => note.id === currentId) : null;
};
export const selectSelectedNotes = (state) => {
  const selectedIds = state.notes.selectedNoteIds;
  return state.notes.notes.filter(note => selectedIds.includes(note.id));
};

export const selectFilteredNotes = createSelector(
  [selectAllNotes, (state) => state.notes.filters, (state) => state.notes.sort],
  (notes, filters, sort) => {
    let filtered = [...notes];

    // Apply filters
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(note =>
        note.title.toLowerCase().includes(searchTerm) ||
        note.content.toLowerCase().includes(searchTerm) ||
        note.tags.some(tag => tag.toLowerCase().includes(searchTerm))
      );
    }

    if (filters.category) {
      filtered = filtered.filter(note => note.category === filters.category);
    }

    if (filters.tags.length > 0) {
      filtered = filtered.filter(note =>
        filters.tags.some(tag => note.tags.includes(tag))
      );
    }

    if (filters.isPinned !== undefined) {
      filtered = filtered.filter(note => note.isPinned === filters.isPinned);
    }

    if (filters.isArchived !== undefined) {
      filtered = filtered.filter(note => note.isArchived === filters.isArchived);
    }

    if (filters.dateRange) {
      const { start, end } = filters.dateRange;
      filtered = filtered.filter(note => {
        const noteDate = new Date(note.updatedAt);
        return noteDate >= start && noteDate <= end;
      });
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let valueA = a[sort.field];
      let valueB = b[sort.field];

      if (sort.field === 'title') {
        valueA = valueA.toLowerCase();
        valueB = valueB.toLowerCase();
      }

      if (sort.order === 'desc') {
        return valueB > valueA ? 1 : valueB < valueA ? -1 : 0;
      } else {
        return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
      }
    });

    return filtered;
  }
);

export const selectNotesStatistics = (state) => state.notes.statistics;
export const selectNotesLoading = (state) => state.notes.loading;
export const selectNotesErrors = (state) => state.notes.errors;
export const selectNotesView = (state) => state.notes.view;

export const selectAvailableCategories = createSelector(
  [selectAllNotes],
  (notes) => {
    const categories = new Set();
    notes.forEach(note => {
      if (note.category) categories.add(note.category);
    });
    return Array.from(categories).sort();
  }
);

export const selectAvailableTags = createSelector(
  [selectAllNotes],
  (notes) => {
    const tags = new Set();
    notes.forEach(note => {
      note.tags.forEach(tag => tags.add(tag));
    });
    return Array.from(tags).sort();
  }
);

export default notesSlice.reducer;