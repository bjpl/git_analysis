import React, { useState, useCallback, useEffect } from 'react';
import { SearchBar } from '../components/ImageSearch/SearchBar';
import { SearchResults } from '../components/ImageSearch/SearchResults';
import { DescriptionPanel } from '../components/DescriptionGenerator/DescriptionPanel';
import { useImageSearch } from '../hooks/useImageSearch';
import { useSelectedImage, useSearchState, useDescriptionState } from '../contexts/AppStateContext';
import { Card } from '../components/Shared/Card/Card';
import { Button } from '../components/Shared/Button/Button';
import { EmptyState } from '../components/Shared/EmptyState/EmptyState';
import { Image, UnsplashImage } from '../types';
import { Search, Sparkles, Filter } from 'lucide-react';
import toast from 'react-hot-toast';

const SearchPage: React.FC = () => {
  const [showDescriptionPanel, setShowDescriptionPanel] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  
  const { selectedImage, selectImage, clearSelection } = useSelectedImage();
  const { 
    searchResults, 
    searchQuery, 
    searchFilters,
    setSearchResults, 
    setSearchQuery,
    setSearchFilters,
    clearSearch 
  } = useSearchState();
  const { resetDescription } = useDescriptionState();

  // Use the image search hook
  const {
    images,
    isLoading,
    error,
    hasMore,
    searchImages,
    loadMore,
    clearResults
  } = useImageSearch();

  // Sync hook results with global state
  useEffect(() => {
    if (images.length !== searchResults.length) {
      setSearchResults(images);
    }
  }, [images, searchResults.length, setSearchResults]);

  const handleSearch = useCallback(async (query: string, filters = searchFilters) => {
    if (!query.trim()) {
      toast.error('Please enter a search term');
      return;
    }

    try {
      setSearchQuery(query);
      setSearchFilters(filters);
      clearSelection();
      resetDescription();
      
      await searchImages({
        query: query.trim(),
        orientation: filters.orientation,
        color: filters.color,
        category: filters.category,
      });
      
      // Close filters after search
      setShowFilters(false);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed. Please try again.');
    }
  }, [searchFilters, setSearchQuery, setSearchFilters, clearSelection, resetDescription, searchImages]);

  const handleImageSelect = useCallback((image: UnsplashImage) => {
    selectImage(image);
    setShowDescriptionPanel(false); // Close any existing panel
    
    // Small delay to allow state update
    setTimeout(() => {
      setShowDescriptionPanel(true);
    }, 100);
  }, [selectImage]);

  const handleGenerateDescription = useCallback((image: UnsplashImage) => {
    selectImage(image);
    setShowDescriptionPanel(true);
  }, [selectImage]);

  const handleCloseDescriptionPanel = useCallback(() => {
    setShowDescriptionPanel(false);
  }, []);

  const handleLoadMore = useCallback(() => {
    if (hasMore && !isLoading) {
      loadMore();
    }
  }, [hasMore, isLoading, loadMore]);

  const handleClearSearch = useCallback(() => {
    clearSearch();
    clearResults();
    clearSelection();
    setShowDescriptionPanel(false);
    setShowFilters(false);
  }, [clearSearch, clearResults, clearSelection]);

  const handleRandomSearch = useCallback(() => {
    const randomTerms = [
      'nature', 'architecture', 'food', 'travel', 'art', 'science',
      'technology', 'animals', 'flowers', 'landscape', 'city', 'ocean'
    ];
    const randomTerm = randomTerms[Math.floor(Math.random() * randomTerms.length)];
    handleSearch(randomTerm);
  }, [handleSearch]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Image Search
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Search for beautiful images and generate AI-powered descriptions to learn new vocabulary.
          </p>
        </div>

        {/* Search Controls */}
        <Card className="p-6 mb-6">
          <div className="space-y-4">
            {/* Main search bar */}
            <div className="flex gap-4">
              <div className="flex-1">
                <SearchBar
                  onSearch={handleSearch}
                  placeholder="Search for images... (e.g., 'mountain landscape', 'city architecture')"
                  defaultValue={searchQuery}
                  isLoading={isLoading}
                />
              </div>
              
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className={showFilters ? 'bg-indigo-50 border-indigo-200' : ''}
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </Button>
            </div>

            {/* Filters */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Orientation
                  </label>
                  <select
                    value={searchFilters.orientation || ''}
                    onChange={(e) => setSearchFilters({ 
                      ...searchFilters, 
                      orientation: e.target.value as any || undefined 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="">Any orientation</option>
                    <option value="landscape">Landscape</option>
                    <option value="portrait">Portrait</option>
                    <option value="squarish">Square</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Color
                  </label>
                  <select
                    value={searchFilters.color || ''}
                    onChange={(e) => setSearchFilters({ 
                      ...searchFilters, 
                      color: e.target.value || undefined 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="">Any color</option>
                    <option value="black_and_white">Black & White</option>
                    <option value="black">Black</option>
                    <option value="white">White</option>
                    <option value="yellow">Yellow</option>
                    <option value="orange">Orange</option>
                    <option value="red">Red</option>
                    <option value="purple">Purple</option>
                    <option value="magenta">Magenta</option>
                    <option value="green">Green</option>
                    <option value="teal">Teal</option>
                    <option value="blue">Blue</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Category
                  </label>
                  <select
                    value={searchFilters.category || ''}
                    onChange={(e) => setSearchFilters({ 
                      ...searchFilters, 
                      category: e.target.value || undefined 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="">Any category</option>
                    <option value="nature">Nature</option>
                    <option value="architecture">Architecture</option>
                    <option value="food">Food</option>
                    <option value="travel">Travel</option>
                    <option value="technology">Technology</option>
                    <option value="people">People</option>
                  </select>
                </div>
              </div>
            )}

            {/* Quick actions */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRandomSearch}
                disabled={isLoading}
              >
                <Sparkles className="w-4 h-4 mr-1" />
                Random Search
              </Button>
              
              {(searchQuery || searchResults.length > 0) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearSearch}
                  disabled={isLoading}
                >
                  Clear Search
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="p-4 mb-6 border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800">
            <div className="text-red-700 dark:text-red-400">
              <strong>Search Error:</strong> {error.message}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSearch(searchQuery)}
              className="mt-2 border-red-300 text-red-700 hover:bg-red-100"
            >
              Try Again
            </Button>
          </Card>
        )}

        {/* Search Results */}
        {searchResults.length > 0 || isLoading ? (
          <SearchResults
            images={searchResults}
            isLoading={isLoading}
            hasMore={hasMore}
            onLoadMore={handleLoadMore}
            onImageSelect={handleImageSelect}
            onGenerateDescription={handleGenerateDescription}
            selectedImageId={selectedImage?.id}
            className="mb-6"
          />
        ) : !isLoading && !error && searchQuery && (
          <EmptyState
            title="No images found"
            description={`No results found for "${searchQuery}". Try different keywords or check your filters.`}
            actionText="Try Random Search"
            onAction={handleRandomSearch}
          />
        )}

        {/* Welcome state when no search has been performed */}
        {!searchQuery && !isLoading && searchResults.length === 0 && (
          <div className="text-center py-16">
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Start your visual vocabulary journey
              </h2>
              
              <p className="text-gray-600 dark:text-gray-300 mb-8">
                Search for images that interest you, then generate AI-powered descriptions 
                to discover new vocabulary words in context.
              </p>

              <div className="space-y-4">
                <Button
                  onClick={handleRandomSearch}
                  size="lg"
                  disabled={isLoading}
                >
                  <Sparkles className="w-5 h-5 mr-2" />
                  Try Random Search
                </Button>
                
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Popular searches: nature, architecture, food, travel, art
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Description Panel */}
      <DescriptionPanel
        image={selectedImage}
        onClose={handleCloseDescriptionPanel}
        isOpen={showDescriptionPanel}
      />
    </div>
  );
};

export default SearchPage;