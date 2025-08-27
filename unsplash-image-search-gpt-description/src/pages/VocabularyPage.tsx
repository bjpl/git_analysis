import React, { useState, useMemo } from 'react';
import { useSearchParams, Outlet, useLocation } from 'react-router-dom';
import { cn } from '@/utils/cn';
import { useVocabulary } from '@/hooks/useVocabulary';
import { VocabularyManager } from '@/components/VocabularyManager/VocabularyManager';
import { VocabularyStats } from '@/components/VocabularyManager/VocabularyStats';
import { VocabularyAnalytics } from '@/components/VocabularyManager/VocabularyAnalytics';
import { EmptyState } from '@/components/Shared/EmptyState/EmptyState';
import { LoadingSkeleton } from '@/components/Shared/LoadingStates/LoadingSkeleton';
import { Button } from '@/components/Shared/Button/Button';
import {
  BookOpenIcon,
  PlusIcon,
  ChartBarIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface VocabularyPageProps {
  className?: string;
}

type ViewMode = 'list' | 'stats' | 'analytics';
type FilterType = 'all' | 'learning' | 'mastered' | 'needs-review';

/**
 * Vocabulary Page - Main vocabulary management interface
 * Features:
 * - Multiple view modes (list, stats, analytics)
 * - Search and filtering capabilities
 * - URL-synced parameters
 * - Nested routing support
 * - Responsive layout
 */
export function VocabularyPage({ className }: VocabularyPageProps) {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [filter, setFilter] = useState<FilterType>((searchParams.get('filter') as FilterType) || 'all');
  const [showAddForm, setShowAddForm] = useState(false);

  const {
    vocabularyItems,
    isLoading,
    error,
    addVocabularyItem,
    updateVocabularyItem,
    deleteVocabularyItem,
    getVocabularyStats
  } = useVocabulary();

  // Check if we're on a nested route
  const isNestedRoute = location.pathname !== '/vocabulary';

  // Update URL params when filters change
  const updateSearchParams = (updates: Record<string, string | null>) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        newParams.set(key, value);
      } else {
        newParams.delete(key);
      }
    });
    
    setSearchParams(newParams);
  };

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    updateSearchParams({ search: query || null });
  };

  // Handle filter change
  const handleFilterChange = (newFilter: FilterType) => {
    setFilter(newFilter);
    updateSearchParams({ filter: newFilter === 'all' ? null : newFilter });
  };

  // Filter vocabulary items
  const filteredItems = useMemo(() => {
    if (!vocabularyItems) return [];

    let filtered = vocabularyItems;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item =>
        item.spanish.toLowerCase().includes(query) ||
        item.english.toLowerCase().includes(query) ||
        item.category?.toLowerCase().includes(query) ||
        item.context?.toLowerCase().includes(query)
      );
    }

    // Apply status filter
    switch (filter) {
      case 'learning':
        filtered = filtered.filter(item => item.masteryLevel < 3);
        break;
      case 'mastered':
        filtered = filtered.filter(item => item.masteryLevel >= 4);
        break;
      case 'needs-review':
        filtered = filtered.filter(item => {
          const daysSinceLastReview = item.lastReviewedAt
            ? (Date.now() - new Date(item.lastReviewedAt).getTime()) / (1000 * 60 * 60 * 24)
            : Infinity;
          return daysSinceLastReview > 7; // Needs review if not reviewed in 7 days
        });
        break;
    }

    return filtered;
  }, [vocabularyItems, searchQuery, filter]);

  // Get vocabulary statistics
  const stats = useMemo(() => {
    if (!vocabularyItems) return null;
    return getVocabularyStats();
  }, [vocabularyItems, getVocabularyStats]);

  // If we're on a nested route, render the outlet
  if (isNestedRoute) {
    return (
      <div className={cn('min-h-screen bg-gray-50 dark:bg-gray-900', className)}>
        <Outlet />
      </div>
    );
  }

  return (
    <div className={cn('min-h-screen bg-gray-50 dark:bg-gray-900', className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              My Vocabulary
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Manage and track your Spanish vocabulary learning progress
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* View Mode Toggles */}
            <div className="flex rounded-lg bg-gray-100 dark:bg-gray-800 p-1">
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  viewMode === 'list'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                )}
              >
                List
              </button>
              <button
                onClick={() => setViewMode('stats')}
                className={cn(
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  viewMode === 'stats'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                )}
              >
                Stats
              </button>
              <button
                onClick={() => setViewMode('analytics')}
                className={cn(
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  viewMode === 'analytics'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                )}
              >
                Analytics
              </button>
            </div>

            {/* Add Vocabulary Button */}
            <Button
              variant="primary"
              size="sm"
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2"
            >
              <PlusIcon className="w-4 h-4" />
              Add Word
            </Button>
          </div>
        </div>

        {/* Search and Filter Bar */}
        {viewMode === 'list' && (
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            {/* Search */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search vocabulary..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className={cn(
                  'w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700',
                  'rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
                  'placeholder-gray-500 dark:placeholder-gray-400',
                  'focus:ring-2 focus:ring-primary-500 focus:border-transparent'
                )}
              />
            </div>

            {/* Filter */}
            <div className="flex items-center gap-2">
              <FunnelIcon className="w-4 h-4 text-gray-400" />
              <select
                value={filter}
                onChange={(e) => handleFilterChange(e.target.value as FilterType)}
                className={cn(
                  'border border-gray-200 dark:border-gray-700 rounded-lg',
                  'bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
                  'px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent'
                )}
              >
                <option value="all">All Words</option>
                <option value="learning">Learning</option>
                <option value="mastered">Mastered</option>
                <option value="needs-review">Needs Review</option>
              </select>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <LoadingSkeleton key={i} className="h-20 w-full rounded-lg" />
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-12">
            <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Failed to Load Vocabulary
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {error.message || 'Something went wrong while loading your vocabulary.'}
            </p>
            <Button
              variant="outline"
              onClick={() => window.location.reload()}
            >
              Try Again
            </Button>
          </div>
        )}

        {/* Main Content */}
        {!isLoading && !error && (
          <>
            {/* List View */}
            {viewMode === 'list' && (
              <>
                {filteredItems.length === 0 && !vocabularyItems?.length && (
                  <EmptyState
                    icon={BookOpenIcon}
                    title="Start Building Your Vocabulary"
                    description="Add Spanish words and phrases to begin your language learning journey."
                    action={{
                      label: 'Add Your First Word',
                      onClick: () => setShowAddForm(true)
                    }}
                  />
                )}

                {filteredItems.length === 0 && vocabularyItems?.length && (
                  <EmptyState
                    icon={MagnifyingGlassIcon}
                    title="No Words Found"
                    description={`No vocabulary items match your current search and filter criteria.`}
                    action={{
                      label: 'Clear Filters',
                      onClick: () => {
                        setSearchQuery('');
                        setFilter('all');
                        updateSearchParams({ search: null, filter: null });
                      }
                    }}
                  />
                )}

                {filteredItems.length > 0 && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                    <VocabularyManager
                      vocabularyItems={filteredItems}
                      onAddItem={addVocabularyItem}
                      onUpdateItem={updateVocabularyItem}
                      onDeleteItem={deleteVocabularyItem}
                      showAddForm={showAddForm}
                      onShowAddFormChange={setShowAddForm}
                    />
                  </div>
                )}
              </>
            )}

            {/* Stats View */}
            {viewMode === 'stats' && stats && (
              <VocabularyStats stats={stats} vocabularyItems={vocabularyItems} />
            )}

            {/* Analytics View */}
            {viewMode === 'analytics' && vocabularyItems && (
              <VocabularyAnalytics vocabularyItems={vocabularyItems} />
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default VocabularyPage;