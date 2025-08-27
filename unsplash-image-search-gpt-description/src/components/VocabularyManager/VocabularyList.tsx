import React, { useState, useMemo, useCallback } from 'react';
import { Search, Filter, Download, Plus, MoreVertical, Eye, EyeOff, Zap } from 'lucide-react';
import { VocabularyItem, VocabularyFilter, MasteryLevel, VocabularySortBy } from '../../types';
import { useVocabulary } from '../../hooks/useVocabulary';
import { VocabularyItem as VocabItem } from './VocabularyItem';
import { AddVocabulary } from './AddVocabulary';
import { ExportDialog } from './ExportDialog';
import { Button } from '../Shared/Button/Button';
import { Modal } from '../Shared/Modal/Modal';
import { Card } from '../Shared/Card/Card';

interface VocabularyListProps {
  className?: string;
  showAddButton?: boolean;
  compactMode?: boolean;
  maxHeight?: string;
}

export function VocabularyList({
  className = '',
  showAddButton = true,
  compactMode = false,
  maxHeight = 'none'
}: VocabularyListProps) {
  const {
    vocabularyItems,
    stats,
    filter,
    setFilter,
    isLoading,
    error,
    bulkDelete,
    bulkUpdate,
    getDueForReview
  } = useVocabulary();

  // Local state
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [showAddModal, setShowAddModal] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState(filter.search || '');
  const [bulkActionMenuOpen, setBulkActionMenuOpen] = useState(false);

  // Memoized filtered and sorted items
  const filteredItems = useMemo(() => {
    let items = [...vocabularyItems];

    // Apply search filter
    if (searchQuery?.trim()) {
      const query = searchQuery.toLowerCase().trim();
      items = items.filter(item =>
        item.word.toLowerCase().includes(query) ||
        item.translation.toLowerCase().includes(query) ||
        item.context?.toLowerCase().includes(query) ||
        item.notes?.toLowerCase().includes(query) ||
        item.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    return items;
  }, [vocabularyItems, searchQuery]);

  const dueForReview = getDueForReview();

  // Event handlers
  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    // Debounce search
    const timeoutId = setTimeout(() => {
      setFilter(prev => ({ ...prev, search: value || undefined }));
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [setFilter]);

  const handleFilterChange = useCallback((newFilter: Partial<VocabularyFilter>) => {
    setFilter(prev => ({ ...prev, ...newFilter }));
  }, [setFilter]);

  const handleSelectItem = useCallback((id: string) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  }, []);

  const handleSelectAll = useCallback(() => {
    if (selectedItems.size === filteredItems.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredItems.map(item => item.id)));
    }
  }, [selectedItems.size, filteredItems]);

  const handleBulkDelete = useCallback(async () => {
    if (selectedItems.size === 0) return;
    
    if (confirm(`Are you sure you want to delete ${selectedItems.size} vocabulary items? This action cannot be undone.`)) {
      await bulkDelete(Array.from(selectedItems));
      setSelectedItems(new Set());
      setBulkActionMenuOpen(false);
    }
  }, [selectedItems, bulkDelete]);

  const handleBulkMasteryUpdate = useCallback(async (masteryLevel: MasteryLevel) => {
    if (selectedItems.size === 0) return;
    
    await bulkUpdate(Array.from(selectedItems), { masteryLevel });
    setSelectedItems(new Set());
    setBulkActionMenuOpen(false);
  }, [selectedItems, bulkUpdate]);

  const handleSort = useCallback((sortBy: VocabularySortBy) => {
    const sortOrder = filter.sortBy === sortBy && filter.sortOrder === 'desc' ? 'asc' : 'desc';
    handleFilterChange({ sortBy, sortOrder });
  }, [filter.sortBy, filter.sortOrder, handleFilterChange]);

  if (error) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="text-center text-red-600">
          <p className="font-medium">Failed to load vocabulary</p>
          <p className="text-sm mt-1">{error.message || 'An error occurred'}</p>
        </div>
      </Card>
    );
  }

  return (
    <div className={`vocabulary-list ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              My Vocabulary
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {stats?.totalWords || 0} words • {dueForReview.length} due for review
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            {dueForReview.length > 0 && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => {/* Navigate to review */}}
                className="bg-orange-500 hover:bg-orange-600"
              >
                <Zap className="w-4 h-4 mr-1" />
                Review ({dueForReview.length})
              </Button>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowExportDialog(true)}
            >
              <Download className="w-4 h-4 mr-1" />
              Export
            </Button>
            
            {showAddButton && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowAddModal(true)}
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Word
              </Button>
            )}
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search words, translations, notes..."
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:border-gray-600 dark:bg-gray-800 dark:text-white"
            />
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className={showFilters ? 'bg-blue-50 text-blue-600 dark:bg-blue-900 dark:text-blue-300' : ''}
          >
            <Filter className="w-4 h-4 mr-1" />
            Filters
          </Button>
        </div>

        {/* Expanded Filters */}
        {showFilters && (
          <Card className="p-4 mb-4 bg-gray-50 dark:bg-gray-800">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Mastery Level Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Mastery Level
                </label>
                <select
                  multiple
                  value={filter.masteryLevel || []}
                  onChange={(e) => {
                    const values = Array.from(e.target.selectedOptions).map(o => o.value as MasteryLevel);
                    handleFilterChange({ masteryLevel: values.length ? values : undefined });
                  }}
                  className="w-full p-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  size={4}
                >
                  <option value={MasteryLevel.NEW}>New</option>
                  <option value={MasteryLevel.LEARNING}>Learning</option>
                  <option value={MasteryLevel.REVIEW}>Review</option>
                  <option value={MasteryLevel.MASTERED}>Mastered</option>
                </select>
              </div>

              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category
                </label>
                <select
                  value={filter.category || ''}
                  onChange={(e) => handleFilterChange({ category: e.target.value || undefined })}
                  className="w-full p-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">All Categories</option>
                  {stats?.categoryBreakdown && Object.keys(stats.categoryBreakdown).map(category => (
                    <option key={category} value={category}>
                      {category} ({stats.categoryBreakdown[category]})
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort Options */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Sort By
                </label>
                <select
                  value={filter.sortBy}
                  onChange={(e) => handleFilterChange({ sortBy: e.target.value as VocabularySortBy })}
                  className="w-full p-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value={VocabularySortBy.CREATED_AT}>Date Added</option>
                  <option value={VocabularySortBy.WORD}>Alphabetical</option>
                  <option value={VocabularySortBy.DIFFICULTY}>Difficulty</option>
                  <option value={VocabularySortBy.TIMES_REVIEWED}>Times Reviewed</option>
                  <option value={VocabularySortBy.ACCURACY}>Accuracy</option>
                  <option value={VocabularySortBy.NEXT_REVIEW}>Next Review</option>
                </select>
              </div>
            </div>
          </Card>
        )}

        {/* Bulk Actions Bar */}
        {selectedItems.size > 0 && (
          <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900 rounded-lg mb-4">
            <span className="text-sm text-blue-700 dark:text-blue-300">
              {selectedItems.size} item{selectedItems.size !== 1 ? 's' : ''} selected
            </span>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkMasteryUpdate(MasteryLevel.MASTERED)}
              >
                Mark as Mastered
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkMasteryUpdate(MasteryLevel.NEW)}
              >
                Reset to New
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleBulkDelete}
                className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900"
              >
                Delete
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedItems(new Set())}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Vocabulary Items List */}
      <div 
        className="vocabulary-items-container"
        style={{ maxHeight, overflowY: maxHeight !== 'none' ? 'auto' : 'visible' }}
      >
        {isLoading && filteredItems.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredItems.length === 0 ? (
          <Card className="p-8 text-center">
            <div className="text-gray-500 dark:text-gray-400">
              {searchQuery ? (
                <div>
                  <p className="font-medium">No vocabulary found</p>
                  <p className="text-sm mt-1">
                    Try adjusting your search or filters
                  </p>
                </div>
              ) : (
                <div>
                  <p className="font-medium">No vocabulary yet</p>
                  <p className="text-sm mt-1 mb-4">
                    Start building your vocabulary by adding words
                  </p>
                  {showAddButton && (
                    <Button
                      variant="primary"
                      onClick={() => setShowAddModal(true)}
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Your First Word
                    </Button>
                  )}
                </div>
              )}
            </div>
          </Card>
        ) : (
          <div className="space-y-3">
            {/* Select All Checkbox */}
            {!compactMode && (
              <div className="flex items-center p-3 border-b border-gray-200 dark:border-gray-700">
                <input
                  type="checkbox"
                  checked={selectedItems.size === filteredItems.length}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <label className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                  Select all ({filteredItems.length})
                </label>
              </div>
            )}
            
            {/* Vocabulary Items */}
            {filteredItems.map((item) => (
              <VocabItem
                key={item.id}
                item={item}
                compactMode={compactMode}
                isSelected={selectedItems.has(item.id)}
                onSelect={() => handleSelectItem(item.id)}
                showSelection={!compactMode}
              />
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add New Vocabulary"
        size="lg"
      >
        <AddVocabulary onClose={() => setShowAddModal(false)} />
      </Modal>

      <Modal
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        title="Export Vocabulary"
        size="md"
      >
        <ExportDialog onClose={() => setShowExportDialog(false)} />
      </Modal>
    </div>
  );
}