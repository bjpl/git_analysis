/**
 * NotesService - Comprehensive notes management service
 * Handles CRUD operations, search, filtering, and export/import functionality
 */

import { notesStorage } from '../utils/notesStorage.js';
import { generateId, sanitizeInput, validateNote } from '../utils/noteHelpers.js';

class NotesService {
  constructor() {
    this.notes = new Map();
    this.listeners = new Set();
    this.isInitialized = false;
    this.operationQueue = [];
    this.isProcessingQueue = false;
  }

  /**
   * Initialize the service and load notes from storage
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      const savedNotes = await notesStorage.loadNotes();
      savedNotes.forEach(note => {
        this.notes.set(note.id, { ...note });
      });
      this.isInitialized = true;
      this.notifyListeners({ type: 'NOTES_LOADED', payload: Array.from(this.notes.values()) });
    } catch (error) {
      console.error('Failed to initialize NotesService:', error);
      throw new Error('Failed to load notes from storage');
    }
  }

  /**
   * Create a new note
   */
  async create(noteData) {
    try {
      const id = generateId();
      const now = new Date().toISOString();
      
      const note = {
        id,
        title: sanitizeInput(noteData.title || 'Untitled Note'),
        content: sanitizeInput(noteData.content || ''),
        tags: noteData.tags ? noteData.tags.map(tag => sanitizeInput(tag)) : [],
        category: sanitizeInput(noteData.category || 'default'),
        createdAt: now,
        updatedAt: now,
        isPinned: Boolean(noteData.isPinned),
        isArchived: Boolean(noteData.isArchived),
        metadata: {
          wordCount: this.countWords(noteData.content || ''),
          readingTime: this.calculateReadingTime(noteData.content || ''),
          ...noteData.metadata
        }
      };

      const validationResult = validateNote(note);
      if (!validationResult.isValid) {
        throw new Error(`Invalid note data: ${validationResult.errors.join(', ')}`);
      }

      // Optimistic update
      this.notes.set(id, note);
      this.notifyListeners({ type: 'NOTE_CREATED', payload: note });

      // Queue storage operation
      await this.queueOperation('create', note);

      return note;
    } catch (error) {
      console.error('Failed to create note:', error);
      throw error;
    }
  }

  /**
   * Read a note by ID
   */
  async read(id) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    const note = this.notes.get(id);
    if (!note) {
      throw new Error(`Note with id ${id} not found`);
    }

    return { ...note };
  }

  /**
   * Update an existing note
   */
  async update(id, updateData) {
    try {
      const existingNote = this.notes.get(id);
      if (!existingNote) {
        throw new Error(`Note with id ${id} not found`);
      }

      const updatedNote = {
        ...existingNote,
        ...updateData,
        id: existingNote.id, // Prevent ID modification
        updatedAt: new Date().toISOString(),
        metadata: {
          ...existingNote.metadata,
          wordCount: this.countWords(updateData.content || existingNote.content),
          readingTime: this.calculateReadingTime(updateData.content || existingNote.content),
          ...updateData.metadata
        }
      };

      // Sanitize inputs
      if (updatedNote.title) updatedNote.title = sanitizeInput(updatedNote.title);
      if (updatedNote.content) updatedNote.content = sanitizeInput(updatedNote.content);
      if (updatedNote.category) updatedNote.category = sanitizeInput(updatedNote.category);
      if (updatedNote.tags) updatedNote.tags = updatedNote.tags.map(tag => sanitizeInput(tag));

      const validationResult = validateNote(updatedNote);
      if (!validationResult.isValid) {
        throw new Error(`Invalid note data: ${validationResult.errors.join(', ')}`);
      }

      // Optimistic update
      this.notes.set(id, updatedNote);
      this.notifyListeners({ type: 'NOTE_UPDATED', payload: updatedNote });

      // Queue storage operation
      await this.queueOperation('update', updatedNote);

      return updatedNote;
    } catch (error) {
      console.error('Failed to update note:', error);
      throw error;
    }
  }

  /**
   * Delete a note by ID
   */
  async delete(id) {
    try {
      const note = this.notes.get(id);
      if (!note) {
        throw new Error(`Note with id ${id} not found`);
      }

      // Optimistic update
      this.notes.delete(id);
      this.notifyListeners({ type: 'NOTE_DELETED', payload: { id, note } });

      // Queue storage operation
      await this.queueOperation('delete', { id });

      return true;
    } catch (error) {
      console.error('Failed to delete note:', error);
      throw error;
    }
  }

  /**
   * Get all notes with optional filtering
   */
  async list(options = {}) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    let notes = Array.from(this.notes.values());

    // Apply filters
    if (options.category) {
      notes = notes.filter(note => note.category === options.category);
    }

    if (options.tags && options.tags.length > 0) {
      notes = notes.filter(note => 
        options.tags.some(tag => note.tags.includes(tag))
      );
    }

    if (options.isPinned !== undefined) {
      notes = notes.filter(note => note.isPinned === options.isPinned);
    }

    if (options.isArchived !== undefined) {
      notes = notes.filter(note => note.isArchived === options.isArchived);
    }

    // Apply search
    if (options.search) {
      const searchTerm = options.search.toLowerCase();
      notes = notes.filter(note =>
        note.title.toLowerCase().includes(searchTerm) ||
        note.content.toLowerCase().includes(searchTerm) ||
        note.tags.some(tag => tag.toLowerCase().includes(searchTerm))
      );
    }

    // Apply sorting
    const sortBy = options.sortBy || 'updatedAt';
    const sortOrder = options.sortOrder || 'desc';
    
    notes.sort((a, b) => {
      let valueA = a[sortBy];
      let valueB = b[sortBy];

      if (sortBy === 'title') {
        valueA = valueA.toLowerCase();
        valueB = valueB.toLowerCase();
      }

      if (sortOrder === 'desc') {
        return valueB > valueA ? 1 : valueB < valueA ? -1 : 0;
      } else {
        return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
      }
    });

    // Apply pagination
    if (options.limit || options.offset) {
      const offset = options.offset || 0;
      const limit = options.limit || notes.length;
      notes = notes.slice(offset, offset + limit);
    }

    return notes;
  }

  /**
   * Search notes with advanced options
   */
  async search(query, options = {}) {
    const searchOptions = {
      search: query,
      ...options
    };

    return this.list(searchOptions);
  }

  /**
   * Batch operations for multiple notes
   */
  async batchOperation(operation, items) {
    const results = [];
    const errors = [];

    for (const item of items) {
      try {
        let result;
        switch (operation) {
          case 'create':
            result = await this.create(item);
            break;
          case 'update':
            result = await this.update(item.id, item);
            break;
          case 'delete':
            result = await this.delete(item.id || item);
            break;
          default:
            throw new Error(`Unknown batch operation: ${operation}`);
        }
        results.push({ success: true, data: result });
      } catch (error) {
        errors.push({ error: error.message, item });
        results.push({ success: false, error: error.message, item });
      }
    }

    return {
      results,
      errors,
      successCount: results.filter(r => r.success).length,
      errorCount: errors.length
    };
  }

  /**
   * Export notes in various formats
   */
  async export(format = 'json', options = {}) {
    try {
      const notes = await this.list(options);
      
      switch (format.toLowerCase()) {
        case 'json':
          return JSON.stringify(notes, null, 2);
        
        case 'markdown':
          return this.exportToMarkdown(notes);
        
        case 'csv':
          return this.exportToCsv(notes);
        
        case 'pdf':
          return this.exportToPdf(notes);
        
        default:
          throw new Error(`Unsupported export format: ${format}`);
      }
    } catch (error) {
      console.error('Failed to export notes:', error);
      throw error;
    }
  }

  /**
   * Import notes from various formats
   */
  async import(data, format = 'json', options = {}) {
    try {
      let notes;
      
      switch (format.toLowerCase()) {
        case 'json':
          notes = JSON.parse(data);
          break;
        
        case 'markdown':
          notes = this.importFromMarkdown(data);
          break;
        
        case 'csv':
          notes = this.importFromCsv(data);
          break;
        
        default:
          throw new Error(`Unsupported import format: ${format}`);
      }

      if (!Array.isArray(notes)) {
        notes = [notes];
      }

      const results = await this.batchOperation('create', notes);
      
      this.notifyListeners({ 
        type: 'NOTES_IMPORTED', 
        payload: { 
          totalImported: results.successCount,
          errors: results.errors 
        } 
      });

      return results;
    } catch (error) {
      console.error('Failed to import notes:', error);
      throw error;
    }
  }

  /**
   * Get statistics about notes
   */
  async getStatistics() {
    const notes = await this.list();
    const categories = {};
    const tags = {};
    let totalWordCount = 0;

    notes.forEach(note => {
      categories[note.category] = (categories[note.category] || 0) + 1;
      note.tags.forEach(tag => {
        tags[tag] = (tags[tag] || 0) + 1;
      });
      totalWordCount += note.metadata.wordCount || 0;
    });

    return {
      totalNotes: notes.length,
      pinnedNotes: notes.filter(n => n.isPinned).length,
      archivedNotes: notes.filter(n => n.isArchived).length,
      categories,
      tags,
      totalWordCount,
      averageWordsPerNote: Math.round(totalWordCount / notes.length) || 0
    };
  }

  // Event system
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners(event) {
    this.listeners.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in notes service listener:', error);
      }
    });
  }

  // Queue system for storage operations
  async queueOperation(operation, data) {
    this.operationQueue.push({ operation, data, timestamp: Date.now() });
    
    if (!this.isProcessingQueue) {
      this.processQueue();
    }
  }

  async processQueue() {
    if (this.isProcessingQueue) return;
    
    this.isProcessingQueue = true;

    try {
      while (this.operationQueue.length > 0) {
        const { operation, data } = this.operationQueue.shift();
        
        try {
          switch (operation) {
            case 'create':
            case 'update':
              await notesStorage.saveNote(data);
              break;
            case 'delete':
              await notesStorage.deleteNote(data.id);
              break;
          }
        } catch (error) {
          console.error('Storage operation failed:', error);
          // Could implement retry logic here
        }
      }
    } finally {
      this.isProcessingQueue = false;
    }
  }

  // Helper methods
  countWords(text) {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  calculateReadingTime(text) {
    const wordsPerMinute = 200;
    const wordCount = this.countWords(text);
    return Math.ceil(wordCount / wordsPerMinute);
  }

  exportToMarkdown(notes) {
    return notes.map(note => {
      let markdown = `# ${note.title}\n\n`;
      
      if (note.tags.length > 0) {
        markdown += `**Tags:** ${note.tags.map(tag => `#${tag}`).join(' ')}\n`;
      }
      
      if (note.category && note.category !== 'default') {
        markdown += `**Category:** ${note.category}\n`;
      }
      
      markdown += `**Created:** ${new Date(note.createdAt).toLocaleDateString()}\n`;
      markdown += `**Updated:** ${new Date(note.updatedAt).toLocaleDateString()}\n\n`;
      markdown += `${note.content}\n\n---\n\n`;
      
      return markdown;
    }).join('');
  }

  exportToCsv(notes) {
    const headers = ['ID', 'Title', 'Content', 'Tags', 'Category', 'Created', 'Updated', 'Pinned', 'Archived'];
    const csvContent = [
      headers.join(','),
      ...notes.map(note => [
        note.id,
        `"${note.title.replace(/"/g, '""')}"`,
        `"${note.content.replace(/"/g, '""')}"`,
        `"${note.tags.join(';')}"`,
        note.category,
        note.createdAt,
        note.updatedAt,
        note.isPinned,
        note.isArchived
      ].join(','))
    ].join('\n');
    
    return csvContent;
  }

  async exportToPdf(notes) {
    // This would require a PDF library like jsPDF
    // For now, return markdown format as placeholder
    return this.exportToMarkdown(notes);
  }

  importFromMarkdown(markdownText) {
    // Basic markdown import - could be enhanced
    const sections = markdownText.split('---').filter(section => section.trim());
    
    return sections.map(section => {
      const lines = section.trim().split('\n');
      const title = lines.find(line => line.startsWith('# '))?.replace('# ', '') || 'Imported Note';
      const content = lines.filter(line => !line.startsWith('#') && !line.startsWith('**')).join('\n').trim();
      
      return {
        title,
        content,
        tags: [],
        category: 'imported'
      };
    });
  }

  importFromCsv(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    return lines.slice(1).map(line => {
      const values = line.split(',');
      return {
        title: values[1]?.replace(/"/g, '') || 'Imported Note',
        content: values[2]?.replace(/"/g, '') || '',
        tags: values[3]?.replace(/"/g, '').split(';').filter(tag => tag.trim()) || [],
        category: values[4] || 'imported'
      };
    }).filter(note => note.title);
  }
}

// Create singleton instance
export const notesService = new NotesService();
export default NotesService;