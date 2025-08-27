import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/utils/cn';
import { useAuth } from '@/hooks/useAuth';
import { useDebounce } from '@/hooks/useDebounce';
import { Button } from '../Shared/Button/Button';
import { UserMenu } from '../Auth/UserMenu';
import {
  MagnifyingGlassIcon,
  Bars3Icon,
  BellIcon,
  CommandLineIcon
} from '@heroicons/react/24/outline';

interface HeaderProps {
  onMenuClick: () => void;
  showMenuButton?: boolean;
  className?: string;
}

interface SearchSuggestion {
  id: string;
  text: string;
  type: 'recent' | 'suggestion' | 'vocabulary';
}

/**
 * Header component with responsive navigation, search, and user menu
 * Includes keyboard shortcuts and accessibility features
 */
export function Header({ onMenuClick, showMenuButton = true, className }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debouncedQuery = useDebounce(searchQuery, 300);
  const searchRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const { user, isAuthenticated } = useAuth();

  // Mock suggestions - in real app, this would come from an API
  const mockSuggestions: SearchSuggestion[] = [
    { id: '1', text: 'nature photography', type: 'recent' },
    { id: '2', text: 'urban landscapes', type: 'recent' },
    { id: '3', text: 'portrait', type: 'suggestion' },
    { id: '4', text: 'architecture', type: 'suggestion' },
    { id: '5', text: 'vocabulary: urban', type: 'vocabulary' },
  ];

  // Handle search suggestions
  useEffect(() => {
    if (debouncedQuery && debouncedQuery.length > 2) {
      // Filter suggestions based on query
      const filtered = mockSuggestions.filter(suggestion =>
        suggestion.text.toLowerCase().includes(debouncedQuery.toLowerCase())
      );
      setSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [debouncedQuery]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd/Ctrl + K to focus search
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        searchRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Handle clicks outside search to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node) &&
        !suggestionsRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
        setSearchFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (searchQuery.trim()) {
      // Handle search - in real app, this would trigger search
      console.log('Searching for:', searchQuery);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setSearchQuery(suggestion.text);
    setShowSuggestions(false);
    // Trigger search
    console.log('Selected suggestion:', suggestion);
  };

  return (
    <header 
      className={cn(
        'sticky top-0 z-30 bg-white/95 dark:bg-gray-900/95',
        'backdrop-blur-sm border-b border-gray-200 dark:border-gray-800',
        'transition-colors duration-200',
        className
      )}
      role="banner"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Left Section: Menu + Logo */}
          <div className="flex items-center gap-4">
            {showMenuButton && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onMenuClick}
                aria-label="Open navigation menu"
                className="lg:hidden"
                id="sidebar-trigger"
              >
                <Bars3Icon className="h-5 w-5" />
              </Button>
            )}
            
            <div className="flex items-center gap-2">
              <CommandLineIcon className="h-8 w-8 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                VocabLens
              </h1>
            </div>
          </div>

          {/* Center Section: Search */}
          <div className="flex-1 max-w-2xl mx-4 relative">
            <form onSubmit={handleSearchSubmit} className="relative">
              <div className="relative">
                <MagnifyingGlassIcon 
                  className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" 
                  aria-hidden="true"
                />
                <input
                  ref={searchRef}
                  type="search"
                  placeholder="Search images... (⌘K)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => {
                    setSearchFocused(true);
                    if (suggestions.length > 0) setShowSuggestions(true);
                  }}
                  className={cn(
                    'w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-gray-800',
                    'border border-gray-200 dark:border-gray-700',
                    'rounded-lg text-sm placeholder-gray-500 dark:placeholder-gray-400',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                    'transition-colors duration-200'
                  )}
                  aria-label="Search images"
                  aria-expanded={showSuggestions}
                  aria-haspopup="listbox"
                  role="combobox"
                />
              </div>
              
              {/* Search Suggestions */}
              {showSuggestions && suggestions.length > 0 && (
                <div
                  ref={suggestionsRef}
                  className={cn(
                    'absolute top-full mt-1 w-full bg-white dark:bg-gray-800',
                    'border border-gray-200 dark:border-gray-700',
                    'rounded-lg shadow-lg max-h-60 overflow-y-auto',
                    'z-50'
                  )}
                  role="listbox"
                  aria-label="Search suggestions"
                >
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={suggestion.id}
                      type="button"
                      onClick={() => handleSuggestionClick(suggestion)}
                      className={cn(
                        'w-full px-4 py-2 text-left text-sm',
                        'hover:bg-gray-50 dark:hover:bg-gray-700',
                        'focus:bg-gray-50 dark:focus:bg-gray-700',
                        'focus:outline-none transition-colors',
                        index === 0 && 'rounded-t-lg',
                        index === suggestions.length - 1 && 'rounded-b-lg'
                      )}
                      role="option"
                      aria-selected={false}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-gray-900 dark:text-white">
                          {suggestion.text}
                        </span>
                        <span className={cn(
                          'text-xs px-2 py-1 rounded-full',
                          suggestion.type === 'recent' && 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
                          suggestion.type === 'suggestion' && 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
                          suggestion.type === 'vocabulary' && 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                        )}>
                          {suggestion.type}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </form>
          </div>

          {/* Right Section: Notifications + User Menu */}
          <div className="flex items-center gap-2">
            {isAuthenticated && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  aria-label="View notifications"
                  className="relative"
                >
                  <BellIcon className="h-5 w-5" />
                  {/* Notification badge */}
                  <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    3
                  </span>
                </Button>
                
                <UserMenu user={user} />
              </>
            )}
            
            {!isAuthenticated && (
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
                <Button variant="primary" size="sm">
                  Sign Up
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}