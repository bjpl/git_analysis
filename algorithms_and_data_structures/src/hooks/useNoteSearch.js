/**
 * Note Search Hook
 * Provides comprehensive search functionality with filters and suggestions
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useDebounce } from './useDebounce.js';
import { notesService } from '../services/NotesService.js';

const INITIAL_SEARCH_STATE = {
  query: '',
  results: [],
  suggestions: [],
  filters: {
    categories: [],
    tags: [],
    dateRange: null,
    isPinned: null,
    isArchived: false,
    contentType: 'all' // 'all', 'title', 'content', 'tags'
  },
  sort: {
    field: 'relevance',
    order: 'desc'
  },
  pagination: {
    page: 0,
    size: 20,
    total: 0,
    hasMore: true
  }
};

const SEARCH_DELAY = 300;
const SUGGESTIONS_LIMIT = 10;

export function useNoteSearch(options = {}) {
  const {
    enableSuggestions = true,
    enableHighlighting = true,
    minQueryLength = 2,
    maxResults = 100
  } = options;

  const [state, setState] = useState(INITIAL_SEARCH_STATE);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);

  // Debounce search query
  const debouncedQuery = useDebounce(state.query, SEARCH_DELAY);

  /**
   * Perform search with current query and filters
   */
  const performSearch = useCallback(async (resetPagination = true) => {
    if (!debouncedQuery || debouncedQuery.length < minQueryLength) {
      setState(prev => ({
        ...prev,
        results: [],
        suggestions: [],
        pagination: { ...prev.pagination, total: 0, hasMore: false }
      }));
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const searchOptions = {
        search: debouncedQuery,
        ...state.filters,
        sortBy: state.sort.field === 'relevance' ? 'updatedAt' : state.sort.field,
        sortOrder: state.sort.order,
        offset: resetPagination ? 0 : state.pagination.page * state.pagination.size,
        limit: state.pagination.size + 1 // Load one extra to check for more
      };

      // Remove null/undefined filters
      Object.keys(searchOptions).forEach(key => {
        if (searchOptions[key] === null || searchOptions[key] === undefined) {
          delete searchOptions[key];
        }
      });

      const results = await notesService.search(debouncedQuery, searchOptions);
      
      // Process results for highlighting and relevance
      const processedResults = enableHighlighting ? 
        highlightSearchResults(results.slice(0, state.pagination.size), debouncedQuery) : 
        results.slice(0, state.pagination.size);

      const hasMore = results.length > state.pagination.size;

      setState(prev => ({
        ...prev,
        results: resetPagination ? processedResults : [...prev.results, ...processedResults],
        pagination: {
          ...prev.pagination,
          page: resetPagination ? 1 : prev.pagination.page + 1,
          total: resetPagination ? processedResults.length : prev.pagination.total + processedResults.length,
          hasMore
        }
      }));

      // Add to search history
      if (!searchHistory.includes(debouncedQuery)) {
        setSearchHistory(prev => [debouncedQuery, ...prev.slice(0, 9)]);
      }

    } catch (error) {
      console.error('Search failed:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, [debouncedQuery, state.filters, state.sort, state.pagination.size, minQueryLength, enableHighlighting, searchHistory]);

  /**
   * Generate search suggestions
   */
  const generateSuggestions = useCallback(async (query) => {
    if (!enableSuggestions || !query || query.length < 1) {
      setState(prev => ({ ...prev, suggestions: [] }));
      return;
    }

    try {
      // Get suggestions from search history
      const historySuggestions = searchHistory
        .filter(item => item.toLowerCase().includes(query.toLowerCase()))
        .slice(0, SUGGESTIONS_LIMIT / 2);

      // Get suggestions from note content
      const allNotes = await notesService.list({ limit: 1000 });
      const contentSuggestions = extractSuggestions(allNotes, query)
        .slice(0, SUGGESTIONS_LIMIT - historySuggestions.length);

      const suggestions = [
        ...historySuggestions.map(text => ({ type: 'history', text })),
        ...contentSuggestions
      ];

      setState(prev => ({ ...prev, suggestions }));

    } catch (error) {
      console.error('Failed to generate suggestions:', error);
    }
  }, [enableSuggestions, searchHistory]);

  /**
   * Update search query
   */
  const setQuery = useCallback((query) => {
    setState(prev => ({
      ...prev,
      query,
      pagination: { ...prev.pagination, page: 0, hasMore: true }
    }));

    // Generate suggestions for partial queries
    if (query && query !== debouncedQuery) {
      generateSuggestions(query);
    }
  }, [debouncedQuery, generateSuggestions]);

  /**
   * Update search filters
   */
  const updateFilters = useCallback((filterUpdate) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...filterUpdate },
      pagination: { ...prev.pagination, page: 0, hasMore: true }
    }));
  }, []);

  /**
   * Update sort options
   */
  const updateSort = useCallback((sortUpdate) => {
    setState(prev => ({
      ...prev,
      sort: { ...prev.sort, ...sortUpdate },
      pagination: { ...prev.pagination, page: 0, hasMore: true }
    }));
  }, []);

  /**
   * Clear search
   */
  const clearSearch = useCallback(() => {
    setState(INITIAL_SEARCH_STATE);
    setError(null);
  }, []);

  /**
   * Load more results
   */
  const loadMore = useCallback(async () => {
    if (!state.pagination.hasMore || isLoading) return;
    await performSearch(false);
  }, [state.pagination.hasMore, isLoading, performSearch]);

  /**
   * Search by suggestion
   */
  const searchBySuggestion = useCallback((suggestion) => {
    setQuery(suggestion.text);
  }, [setQuery]);

  /**
   * Quick search by category
   */
  const searchByCategory = useCallback((category) => {
    updateFilters({ categories: [category] });
    setQuery('');
  }, [updateFilters, setQuery]);

  /**
   * Quick search by tag
   */
  const searchByTag = useCallback((tag) => {
    updateFilters({ tags: [tag] });
    setQuery('');
  }, [updateFilters, setQuery]);

  /**
   * Advanced search with multiple criteria
   */
  const advancedSearch = useCallback((criteria) => {
    setState(prev => ({
      ...prev,
      query: criteria.query || '',
      filters: { ...prev.filters, ...criteria.filters },
      sort: { ...prev.sort, ...criteria.sort },
      pagination: { ...prev.pagination, page: 0, hasMore: true }
    }));
  }, []);

  /**
   * Get search statistics
   */
  const getSearchStats = useCallback(async () => {
    try {
      const allNotes = await notesService.list({ limit: 10000 });
      
      const categories = [...new Set(allNotes.map(note => note.category))];
      const tags = [...new Set(allNotes.flatMap(note => note.tags))];
      
      const dateRanges = {
        today: allNotes.filter(note => 
          new Date(note.updatedAt).toDateString() === new Date().toDateString()
        ).length,
        thisWeek: allNotes.filter(note => {
          const noteDate = new Date(note.updatedAt);
          const weekAgo = new Date();
          weekAgo.setDate(weekAgo.getDate() - 7);
          return noteDate >= weekAgo;
        }).length,
        thisMonth: allNotes.filter(note => {
          const noteDate = new Date(note.updatedAt);
          const monthAgo = new Date();
          monthAgo.setMonth(monthAgo.getMonth() - 1);
          return noteDate >= monthAgo;
        }).length
      };

      return {
        totalNotes: allNotes.length,
        categories: categories.map(cat => ({
          name: cat,
          count: allNotes.filter(note => note.category === cat).length
        })),
        tags: tags.map(tag => ({
          name: tag,
          count: allNotes.filter(note => note.tags.includes(tag)).length
        })),
        dateRanges
      };

    } catch (error) {
      console.error('Failed to get search stats:', error);
      return null;
    }
  }, []);

  // Perform search when query or filters change
  useEffect(() => {
    performSearch(true);
  }, [debouncedQuery, state.filters, state.sort]);

  // Memoized computed values
  const hasResults = useMemo(() => state.results.length > 0, [state.results.length]);
  const hasQuery = useMemo(() => debouncedQuery.length >= minQueryLength, [debouncedQuery, minQueryLength]);
  const isEmpty = useMemo(() => hasQuery && !isLoading && !hasResults, [hasQuery, isLoading, hasResults]);
  
  const activeFiltersCount = useMemo(() => {
    return Object.entries(state.filters).reduce((count, [key, value]) => {
      if (key === 'isArchived' && value === false) return count; // Default value
      if (value === null || value === undefined) return count;
      if (Array.isArray(value) && value.length === 0) return count;
      if (key === 'contentType' && value === 'all') return count; // Default value
      return count + 1;
    }, 0);
  }, [state.filters]);

  return {
    // State
    query: state.query,
    results: state.results,
    suggestions: state.suggestions,
    filters: state.filters,
    sort: state.sort,
    pagination: state.pagination,
    isLoading,
    error,
    searchHistory,

    // Computed
    hasResults,
    hasQuery,
    isEmpty,
    activeFiltersCount,
    resultsCount: state.results.length,

    // Actions
    setQuery,
    updateFilters,
    updateSort,
    clearSearch,
    loadMore,
    searchBySuggestion,
    searchByCategory,
    searchByTag,
    advancedSearch,
    getSearchStats,

    // Status
    canLoadMore: state.pagination.hasMore && !isLoading,
    isSearching: isLoading && state.pagination.page === 0
  };
}

// Helper functions
function highlightSearchResults(results, query) {
  const queryWords = query.toLowerCase().split(/\s+/).filter(word => word.length > 0);
  
  return results.map(note => ({
    ...note,
    highlighted: {
      title: highlightText(note.title, queryWords),
      content: highlightText(note.content, queryWords, 150), // Truncate content
      tags: note.tags.map(tag => highlightText(tag, queryWords))
    },
    relevanceScore: calculateRelevance(note, queryWords)
  })).sort((a, b) => b.relevanceScore - a.relevanceScore);
}

function highlightText(text, queryWords, maxLength = null) {
  if (!text) return '';
  
  let highlighted = text;
  queryWords.forEach(word => {
    const regex = new RegExp(`(${word})`, 'gi');
    highlighted = highlighted.replace(regex, '<mark>$1</mark>');
  });

  if (maxLength && highlighted.length > maxLength) {
    // Try to truncate around highlighted content
    const markIndex = highlighted.indexOf('<mark>');
    if (markIndex !== -1) {
      const start = Math.max(0, markIndex - Math.floor(maxLength / 2));
      highlighted = '...' + highlighted.substr(start, maxLength) + '...';
    } else {
      highlighted = highlighted.substr(0, maxLength) + '...';
    }
  }

  return highlighted;
}

function calculateRelevance(note, queryWords) {
  let score = 0;
  
  queryWords.forEach(word => {
    const titleMatches = (note.title.toLowerCase().match(new RegExp(word, 'g')) || []).length;
    const contentMatches = (note.content.toLowerCase().match(new RegExp(word, 'g')) || []).length;
    const tagMatches = note.tags.filter(tag => 
      tag.toLowerCase().includes(word)
    ).length;

    score += titleMatches * 10; // Title matches are most important
    score += contentMatches * 2;
    score += tagMatches * 5;
  });

  // Boost score for exact phrase matches
  const fullQuery = queryWords.join(' ');
  if (note.title.toLowerCase().includes(fullQuery)) score += 20;
  if (note.content.toLowerCase().includes(fullQuery)) score += 10;

  return score;
}

function extractSuggestions(notes, query) {
  const suggestions = new Set();
  const queryLower = query.toLowerCase();

  notes.forEach(note => {
    // Extract words from title and content
    const words = [
      ...note.title.split(/\s+/),
      ...note.content.split(/\s+/),
      ...note.tags
    ];

    words.forEach(word => {
      const cleanWord = word.toLowerCase().replace(/[^\w]/g, '');
      if (cleanWord.length > 2 && cleanWord.includes(queryLower)) {
        suggestions.add({ type: 'word', text: cleanWord });
      }
    });

    // Extract phrases containing the query
    const sentences = note.content.split(/[.!?]+/);
    sentences.forEach(sentence => {
      if (sentence.toLowerCase().includes(queryLower)) {
        const words = sentence.trim().split(/\s+/).slice(0, 5);
        if (words.length > 1) {
          suggestions.add({ type: 'phrase', text: words.join(' ') });
        }
      }
    });
  });

  return Array.from(suggestions).slice(0, SUGGESTIONS_LIMIT);
}