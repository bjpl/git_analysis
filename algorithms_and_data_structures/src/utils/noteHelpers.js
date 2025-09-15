/**
 * Note Helper Utilities
 * Common utility functions for note operations
 */

/**
 * Generate a unique ID for notes
 */
export function generateId() {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 15);
  return `note_${timestamp}_${randomPart}`;
}

/**
 * Sanitize input text to prevent XSS and ensure data integrity
 */
export function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return String(input || '');
  }

  // Remove HTML tags except safe ones
  const allowedTags = ['b', 'i', 'em', 'strong', 'code', 'pre', 'blockquote'];
  const tagRegex = /<\/?([a-zA-Z][a-zA-Z0-9]*)\b[^<>]*>/gi;
  
  let sanitized = input.replace(tagRegex, (match, tagName) => {
    if (allowedTags.includes(tagName.toLowerCase())) {
      return match;
    }
    return '';
  });

  // Decode HTML entities
  sanitized = sanitized
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");

  // Remove potentially dangerous characters
  sanitized = sanitized.replace(/[\x00-\x1f\x7f-\x9f]/g, '');

  return sanitized.trim();
}

/**
 * Validate note data structure
 */
export function validateNote(note) {
  const errors = [];

  // Required fields
  if (!note || typeof note !== 'object') {
    return { isValid: false, errors: ['Note must be an object'] };
  }

  // Title validation
  if (!note.title || typeof note.title !== 'string') {
    errors.push('Title is required and must be a string');
  } else if (note.title.length > 500) {
    errors.push('Title must be less than 500 characters');
  } else if (note.title.trim().length === 0) {
    errors.push('Title cannot be empty');
  }

  // Content validation
  if (note.content !== undefined && typeof note.content !== 'string') {
    errors.push('Content must be a string');
  } else if (note.content && note.content.length > 10000000) { // 10MB limit
    errors.push('Content must be less than 10MB');
  }

  // Tags validation
  if (note.tags !== undefined) {
    if (!Array.isArray(note.tags)) {
      errors.push('Tags must be an array');
    } else {
      if (note.tags.length > 50) {
        errors.push('Maximum 50 tags allowed');
      }
      
      note.tags.forEach((tag, index) => {
        if (typeof tag !== 'string') {
          errors.push(`Tag at index ${index} must be a string`);
        } else if (tag.length > 50) {
          errors.push(`Tag at index ${index} must be less than 50 characters`);
        } else if (tag.trim().length === 0) {
          errors.push(`Tag at index ${index} cannot be empty`);
        }
      });

      // Check for duplicate tags
      const uniqueTags = new Set(note.tags.map(tag => tag.toLowerCase()));
      if (uniqueTags.size !== note.tags.length) {
        errors.push('Duplicate tags are not allowed');
      }
    }
  }

  // Category validation
  if (note.category !== undefined) {
    if (typeof note.category !== 'string') {
      errors.push('Category must be a string');
    } else if (note.category.length > 100) {
      errors.push('Category must be less than 100 characters');
    }
  }

  // Boolean field validation
  if (note.isPinned !== undefined && typeof note.isPinned !== 'boolean') {
    errors.push('isPinned must be a boolean');
  }

  if (note.isArchived !== undefined && typeof note.isArchived !== 'boolean') {
    errors.push('isArchived must be a boolean');
  }

  // Date validation
  if (note.createdAt !== undefined) {
    const createdDate = new Date(note.createdAt);
    if (isNaN(createdDate.getTime())) {
      errors.push('createdAt must be a valid date');
    }
  }

  if (note.updatedAt !== undefined) {
    const updatedDate = new Date(note.updatedAt);
    if (isNaN(updatedDate.getTime())) {
      errors.push('updatedAt must be a valid date');
    }
  }

  // Metadata validation
  if (note.metadata !== undefined) {
    if (typeof note.metadata !== 'object' || note.metadata === null) {
      errors.push('Metadata must be an object');
    } else {
      // Check metadata size
      const metadataStr = JSON.stringify(note.metadata);
      if (metadataStr.length > 100000) { // 100KB limit
        errors.push('Metadata must be less than 100KB');
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Create a default note structure
 */
export function createDefaultNote(overrides = {}) {
  const now = new Date().toISOString();
  
  return {
    id: generateId(),
    title: 'Untitled Note',
    content: '',
    tags: [],
    category: 'default',
    isPinned: false,
    isArchived: false,
    createdAt: now,
    updatedAt: now,
    metadata: {
      wordCount: 0,
      readingTime: 0,
      version: 1
    },
    ...overrides
  };
}

/**
 * Deep clone a note object
 */
export function cloneNote(note) {
  if (!note || typeof note !== 'object') {
    return null;
  }

  return {
    ...note,
    tags: [...(note.tags || [])],
    metadata: { ...(note.metadata || {}) }
  };
}

/**
 * Compare two notes for equality
 */
export function notesEqual(note1, note2) {
  if (!note1 || !note2) return false;
  
  // Compare basic fields
  const fields = ['id', 'title', 'content', 'category', 'isPinned', 'isArchived'];
  for (const field of fields) {
    if (note1[field] !== note2[field]) return false;
  }

  // Compare tags arrays
  if (!arraysEqual(note1.tags || [], note2.tags || [])) return false;

  // Compare metadata objects
  if (!objectsEqual(note1.metadata || {}, note2.metadata || {})) return false;

  return true;
}

/**
 * Extract and clean tags from text
 */
export function extractTags(text) {
  if (!text || typeof text !== 'string') return [];

  // Extract hashtags
  const hashtagRegex = /#(\w+)/g;
  const hashtags = [];
  let match;

  while ((match = hashtagRegex.exec(text)) !== null) {
    hashtags.push(match[1].toLowerCase());
  }

  // Remove duplicates and return
  return [...new Set(hashtags)];
}

/**
 * Generate note excerpt
 */
export function generateExcerpt(content, maxLength = 150) {
  if (!content || typeof content !== 'string') return '';

  // Remove markdown formatting
  let excerpt = content
    .replace(/#{1,6}\s+/g, '') // Headers
    .replace(/\*\*([^*]+)\*\*/g, '$1') // Bold
    .replace(/\*([^*]+)\*/g, '$1') // Italic
    .replace(/`([^`]+)`/g, '$1') // Inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
    .replace(/^\s*[-*+]\s+/gm, '') // Lists
    .replace(/^\s*\d+\.\s+/gm, '') // Numbered lists
    .replace(/\n+/g, ' ') // Multiple newlines
    .trim();

  if (excerpt.length <= maxLength) return excerpt;

  // Truncate at word boundary
  const truncated = excerpt.substring(0, maxLength);
  const lastSpace = truncated.lastIndexOf(' ');
  
  return lastSpace > 0 ? truncated.substring(0, lastSpace) + '...' : truncated + '...';
}

/**
 * Calculate reading time estimate
 */
export function calculateReadingTime(content, wordsPerMinute = 200) {
  if (!content || typeof content !== 'string') return 0;

  const wordCount = countWords(content);
  return Math.max(1, Math.ceil(wordCount / wordsPerMinute));
}

/**
 * Count words in text
 */
export function countWords(text) {
  if (!text || typeof text !== 'string') return 0;

  // Remove markdown and count words
  const cleanText = text
    .replace(/```[\s\S]*?```/g, '') // Code blocks
    .replace(/`[^`]+`/g, '') // Inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
    .replace(/[#*_~`]/g, '') // Markdown formatting
    .replace(/\s+/g, ' ') // Multiple spaces
    .trim();

  if (!cleanText) return 0;

  return cleanText.split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Format date for display
 */
export function formatDate(date, format = 'relative') {
  if (!date) return '';

  const d = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(d.getTime())) return '';

  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  switch (format) {
    case 'relative':
      if (diffMinutes < 1) return 'Just now';
      if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
      return d.toLocaleDateString();

    case 'short':
      return d.toLocaleDateString();

    case 'long':
      return d.toLocaleString();

    case 'iso':
      return d.toISOString();

    default:
      return d.toString();
  }
}

/**
 * Search notes with ranking
 */
export function searchNotes(notes, query, options = {}) {
  if (!query || !Array.isArray(notes)) return notes;

  const {
    fields = ['title', 'content', 'tags'],
    caseSensitive = false,
    exact = false,
    minScore = 0.1
  } = options;

  const searchTerm = caseSensitive ? query : query.toLowerCase();
  const results = [];

  notes.forEach(note => {
    let score = 0;

    fields.forEach(field => {
      let fieldValue = '';
      
      switch (field) {
        case 'title':
          fieldValue = note.title || '';
          break;
        case 'content':
          fieldValue = note.content || '';
          break;
        case 'tags':
          fieldValue = (note.tags || []).join(' ');
          break;
        case 'category':
          fieldValue = note.category || '';
          break;
      }

      if (!caseSensitive) {
        fieldValue = fieldValue.toLowerCase();
      }

      if (exact) {
        if (fieldValue.includes(searchTerm)) {
          score += field === 'title' ? 10 : field === 'tags' ? 5 : 1;
        }
      } else {
        const words = searchTerm.split(/\s+/).filter(w => w.length > 0);
        words.forEach(word => {
          const matches = (fieldValue.match(new RegExp(word, 'g')) || []).length;
          score += matches * (field === 'title' ? 10 : field === 'tags' ? 5 : 1);
        });
      }
    });

    if (score >= minScore) {
      results.push({ note, score });
    }
  });

  return results
    .sort((a, b) => b.score - a.score)
    .map(result => result.note);
}

/**
 * Group notes by a field
 */
export function groupNotes(notes, field) {
  if (!Array.isArray(notes) || !field) return {};

  const groups = {};

  notes.forEach(note => {
    let key;
    
    switch (field) {
      case 'category':
        key = note.category || 'Uncategorized';
        break;
      case 'date':
        key = formatDate(note.createdAt, 'short');
        break;
      case 'tags':
        // Group by each tag
        (note.tags || []).forEach(tag => {
          if (!groups[tag]) groups[tag] = [];
          groups[tag].push(note);
        });
        return;
      case 'pinned':
        key = note.isPinned ? 'Pinned' : 'Unpinned';
        break;
      case 'archived':
        key = note.isArchived ? 'Archived' : 'Active';
        break;
      default:
        key = note[field] || 'Unknown';
    }

    if (!groups[key]) groups[key] = [];
    groups[key].push(note);
  });

  return groups;
}

// Helper functions
function arraysEqual(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;
  
  const sorted1 = [...arr1].sort();
  const sorted2 = [...arr2].sort();
  
  return sorted1.every((item, index) => item === sorted2[index]);
}

function objectsEqual(obj1, obj2) {
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  return keys1.every(key => obj1[key] === obj2[key]);
}