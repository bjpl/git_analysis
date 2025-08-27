import React, { useState, useRef, useEffect } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { SearchBarProps } from '../../types';
import { Button } from '../Shared/Button/Button';
import { useDebounce } from '../../hooks/useDebounce';

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  isLoading,
  suggestions = [],
  placeholder = "Search for images..."
}) => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  
  const debouncedQuery = useDebounce(query, 300);

  // Trigger search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.trim()) {
      onSearch(debouncedQuery.trim());
    }
  }, [debouncedQuery, onSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
      setShowSuggestions(false);
      inputRef.current?.blur();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setShowSuggestions(value.length > 0 && suggestions.length > 0);
    setSelectedSuggestionIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        if (selectedSuggestionIndex >= 0) {
          e.preventDefault();
          handleSuggestionClick(suggestions[selectedSuggestionIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    onSearch(suggestion);
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    inputRef.current?.blur();
  };

  const clearSearch = () => {
    setQuery('');
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const handleFocus = () => {
    if (query.length > 0 && suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleBlur = () => {
    // Delay hiding suggestions to allow clicking on them
    setTimeout(() => {
      setShowSuggestions(false);
      setSelectedSuggestionIndex(-1);
    }, 150);
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <MagnifyingGlassIcon className="absolute left-3 h-5 w-5 text-gray-400 dark:text-gray-500 pointer-events-none" />
          
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder={placeholder}
            className="w-full pl-10 pr-20 py-3 text-base border border-gray-300 dark:border-gray-600 rounded-lg 
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     placeholder-gray-500 dark:placeholder-gray-400
                     focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent
                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
            autoComplete="off"
            spellCheck="false"
            aria-label="Search for images"
            aria-expanded={showSuggestions}
            aria-haspopup="listbox"
            role="combobox"
            aria-autocomplete="list"
          />

          <div className="absolute right-2 flex items-center space-x-1">
            {query && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={clearSearch}
                className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
                aria-label="Clear search"
              >
                <XMarkIcon className="h-4 w-4" />
              </Button>
            )}
            
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={isLoading || !query.trim()}
              className="px-3 py-1.5"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
              ) : (
                'Search'
              )}
            </Button>
          </div>
        </div>

        {/* Search Suggestions */}
        {showSuggestions && suggestions.length > 0 && (
          <div
            ref={suggestionsRef}
            className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 
                     rounded-lg shadow-lg max-h-60 overflow-y-auto"
            role="listbox"
            aria-label="Search suggestions"
          >
            {suggestions.map((suggestion, index) => (
              <button
                key={`${suggestion}-${index}`}
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                className={`w-full text-left px-4 py-2 text-sm transition-colors
                  ${index === selectedSuggestionIndex
                    ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }
                  ${index === 0 ? 'rounded-t-lg' : ''}
                  ${index === suggestions.length - 1 ? 'rounded-b-lg' : ''}
                `}
                role="option"
                aria-selected={index === selectedSuggestionIndex}
              >
                <MagnifyingGlassIcon className="inline h-4 w-4 mr-2 text-gray-400 dark:text-gray-500" />
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </form>

      {/* Search Tips */}
      {!query && !isLoading && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            Try searching for: nature, architecture, people, food, or abstract
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {['Nature', 'Architecture', 'People', 'Food', 'Abstract'].map((tip) => (
              <button
                key={tip}
                onClick={() => {
                  setQuery(tip.toLowerCase());
                  onSearch(tip.toLowerCase());
                }}
                className="px-3 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 
                         rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {tip}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};