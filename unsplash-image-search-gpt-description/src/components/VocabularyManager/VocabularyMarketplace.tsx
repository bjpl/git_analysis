import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  Star,
  Users,
  BookOpen,
  Zap,
  TrendingUp,
  Globe,
  Share,
  Eye,
  Heart,
  MessageCircle,
  Award,
  Clock
} from 'lucide-react';
import { SharedVocabularyList, VocabularyMarketplace } from '../../types';
import { vocabularyService } from '../../services/vocabularyService';
import { useVocabulary } from '../../hooks/useVocabulary';
import { Card } from '../Shared/Card/Card';
import { Button } from '../Shared/Button/Button';
import { Modal } from '../Shared/Modal/Modal';

interface VocabularyMarketplaceProps {
  className?: string;
}

export function VocabularyMarketplaceComponent({ className = '' }: VocabularyMarketplaceProps) {
  const { addVocabularyItem } = useVocabulary();
  const [marketplace, setMarketplace] = useState<VocabularyMarketplace | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [sortBy, setSortBy] = useState<'popular' | 'recent' | 'rating'>('popular');
  const [selectedList, setSelectedList] = useState<SharedVocabularyList | null>(null);
  const [showListModal, setShowListModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [isImporting, setIsImporting] = useState(false);

  useEffect(() => {
    loadMarketplace();
  }, []);

  const loadMarketplace = async () => {
    try {
      const lists = await vocabularyService.getSharedVocabularyLists();
      
      // Extract categories from lists
      const categories = Array.from(new Set(lists.map(list => list.category).filter(Boolean)));
      const popularTags = extractPopularTags(lists);
      const featuredLists = lists.filter(list => list.rating >= 4.5).slice(0, 5);
      
      setMarketplace({
        lists,
        categories,
        popularTags,
        featuredLists
      });
    } catch (error) {
      console.error('Failed to load marketplace:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImportList = async (list: SharedVocabularyList) => {
    setIsImporting(true);
    
    try {
      // Import all vocabulary items from the shared list
      const importPromises = list.items.map(item => 
        addVocabularyItem({
          ...item,
          sharedFromUserId: list.ownerId,
          // Reset learning progress for imported items
          timesReviewed: 0,
          timesCorrect: 0,
          streak: 0,
          lastReviewedAt: undefined,
          nextReviewAt: undefined
        })
      );
      
      await Promise.all(importPromises);
      
      // Update download count
      // This would typically be done on the server
      
      alert(`Successfully imported ${list.items.length} vocabulary items!`);
      setShowListModal(false);
    } catch (error) {
      console.error('Failed to import list:', error);
      alert('Failed to import vocabulary list. Please try again.');
    } finally {
      setIsImporting(false);
    }
  };

  const filteredAndSortedLists = React.useMemo(() => {
    if (!marketplace) return [];
    
    let filtered = marketplace.lists;
    
    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(list =>
        list.name.toLowerCase().includes(query) ||
        list.description?.toLowerCase().includes(query) ||
        list.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    // Apply category filter
    if (selectedCategory) {
      filtered = filtered.filter(list => list.category === selectedCategory);
    }
    
    // Apply sorting
    switch (sortBy) {
      case 'popular':
        return filtered.sort((a, b) => b.downloadCount - a.downloadCount);
      case 'recent':
        return filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
      case 'rating':
        return filtered.sort((a, b) => b.rating - a.rating);
      default:
        return filtered;
    }
  }, [marketplace, searchQuery, selectedCategory, sortBy]);

  if (isLoading) {
    return (
      <div className={`vocabulary-marketplace ${className}`}>
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!marketplace) {
    return (
      <div className={`vocabulary-marketplace ${className}`}>
        <div className="text-center py-12">
          <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Marketplace Unavailable
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Unable to load the vocabulary marketplace. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`vocabulary-marketplace ${className}`}>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Vocabulary Marketplace
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Discover and share vocabulary collections with the community
            </p>
          </div>
          
          <Button
            variant="primary"
            onClick={() => setShowShareModal(true)}
          >
            <Share className="w-4 h-4 mr-2" />
            Share Your List
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search vocabulary lists..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:border-gray-600 dark:bg-gray-800 dark:text-white"
            />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          >
            <option value="">All Categories</option>
            {marketplace.categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          >
            <option value="popular">Most Popular</option>
            <option value="recent">Most Recent</option>
            <option value="rating">Highest Rated</option>
          </select>
        </div>
      </div>

      {/* Featured Lists */}
      {marketplace.featuredLists.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-5 h-5 text-yellow-500" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Featured Collections
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {marketplace.featuredLists.map(list => (
              <VocabularyListCard
                key={list.id}
                list={list}
                onView={() => {
                  setSelectedList(list);
                  setShowListModal(true);
                }}
                featured
              />
            ))}
          </div>
        </div>
      )}

      {/* All Lists */}
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          All Collections ({filteredAndSortedLists.length})
        </h2>
        
        {filteredAndSortedLists.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No Results Found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Try adjusting your search terms or filters
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedLists.map(list => (
              <VocabularyListCard
                key={list.id}
                list={list}
                onView={() => {
                  setSelectedList(list);
                  setShowListModal(true);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* List Detail Modal */}
      <Modal
        isOpen={showListModal}
        onClose={() => setShowListModal(false)}
        title="Vocabulary Collection"
        size="lg"
      >
        {selectedList && (
          <div className="space-y-6">
            {/* List Header */}
            <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {selectedList.name}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {selectedList.description}
                  </p>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {selectedList.ownerName}
                    </span>
                    <span className="flex items-center gap-1">
                      <BookOpen className="w-4 h-4" />
                      {selectedList.items.length} words
                    </span>
                    <span className="flex items-center gap-1">
                      <Download className="w-4 h-4" />
                      {selectedList.downloadCount} downloads
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="w-4 h-4" />
                      {selectedList.rating.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Tags */}
              {selectedList.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedList.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs dark:bg-blue-900 dark:text-blue-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              <Button
                variant="primary"
                onClick={() => handleImportList(selectedList)}
                disabled={isImporting}
                className="w-full"
              >
                {isImporting ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Importing...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Import {selectedList.items.length} Words
                  </div>
                )}
              </Button>
            </div>
            
            {/* Vocabulary Preview */}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                Vocabulary Preview
              </h3>
              
              <div className="max-h-64 overflow-y-auto space-y-2">
                {selectedList.items.slice(0, 20).map((item, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                  >
                    <div>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {item.word}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400 ml-2">
                        → {item.translation}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      Level {item.difficulty}
                    </span>
                  </div>
                ))}
                
                {selectedList.items.length > 20 && (
                  <div className="text-center text-sm text-gray-500 dark:text-gray-400 py-2">
                    ... and {selectedList.items.length - 20} more words
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Share Modal - placeholder for now */}
      <Modal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        title="Share Your Vocabulary"
        size="md"
      >
        <div className="text-center py-8">
          <Share className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Coming Soon!
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            The ability to share your vocabulary lists will be available in a future update.
          </p>
        </div>
      </Modal>
    </div>
  );
}

// Vocabulary List Card Component
interface VocabularyListCardProps {
  list: SharedVocabularyList;
  onView: () => void;
  featured?: boolean;
}

function VocabularyListCard({ list, onView, featured = false }: VocabularyListCardProps) {
  return (
    <Card className={`p-6 hover:shadow-lg transition-all cursor-pointer ${
      featured ? 'ring-2 ring-yellow-400 bg-yellow-50 dark:bg-yellow-900' : ''
    }`} onClick={onView}>
      {featured && (
        <div className="flex items-center gap-1 text-yellow-600 dark:text-yellow-400 mb-3">
          <Award className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase tracking-wide">Featured</span>
        </div>
      )}
      
      <div className="mb-4">
        <h3 className="font-bold text-gray-900 dark:text-white mb-2 line-clamp-2">
          {list.name}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
          {list.description || 'No description provided'}
        </p>
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <BookOpen className="w-4 h-4" />
            {list.items.length}
          </span>
          <span className="flex items-center gap-1">
            <Star className="w-4 h-4" />
            {list.rating.toFixed(1)}
          </span>
        </div>
        
        <span className="flex items-center gap-1">
          <Download className="w-4 h-4" />
          {list.downloadCount}
        </span>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <Users className="w-3 h-3" />
          <span>{list.ownerName}</span>
        </div>
        
        {list.category && (
          <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs dark:bg-gray-700 dark:text-gray-300">
            {list.category}
          </span>
        )}
      </div>
      
      {list.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {list.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs dark:bg-blue-900 dark:text-blue-300"
            >
              {tag}
            </span>
          ))}
          {list.tags.length > 3 && (
            <span className="text-xs text-gray-400">+{list.tags.length - 3}</span>
          )}
        </div>
      )}
    </Card>
  );
}

// Helper function to extract popular tags
function extractPopularTags(lists: SharedVocabularyList[]): string[] {
  const tagCounts = lists.reduce((acc, list) => {
    list.tags.forEach(tag => {
      acc[tag] = (acc[tag] || 0) + 1;
    });
    return acc;
  }, {} as Record<string, number>);
  
  return Object.entries(tagCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 20)
    .map(([tag]) => tag);
}