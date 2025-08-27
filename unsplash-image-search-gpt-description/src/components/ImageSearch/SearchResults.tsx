import React, { useCallback, useMemo } from 'react';
import { FixedSizeGrid as Grid } from 'react-window';
import InfiniteLoader from 'react-window-infinite-loader';
import { useWindowSize } from '../../hooks/useWindowSize';
import { Image } from '../../types';
import { ImageCard } from './ImageCard';
import { LoadingSkeleton } from '../Shared/LoadingStates/LoadingSkeleton';
import { EmptyState } from '../Shared/EmptyState/EmptyState';

interface SearchResultsProps {
  images: Image[];
  isLoading: boolean;
  hasMore: boolean;
  onLoadMore: () => void;
  onImageSelect: (image: Image) => void;
  onGenerateDescription: (image: Image) => void;
  selectedImageId?: string;
  className?: string;
}

interface GridItemProps {
  columnIndex: number;
  rowIndex: number;
  style: React.CSSProperties;
  data: {
    images: Image[];
    columnsPerRow: number;
    onImageSelect: (image: Image) => void;
    onGenerateDescription: (image: Image) => void;
    selectedImageId?: string;
    isLoading: boolean;
  };
}

const GridItem: React.FC<GridItemProps> = ({ columnIndex, rowIndex, style, data }) => {
  const { images, columnsPerRow, onImageSelect, onGenerateDescription, selectedImageId, isLoading } = data;
  const index = rowIndex * columnsPerRow + columnIndex;
  const image = images[index];

  if (!image) {
    return (
      <div style={style} className="p-2">
        {isLoading ? (
          <LoadingSkeleton className="w-full aspect-square rounded-lg" />
        ) : null}
      </div>
    );
  }

  return (
    <div style={style} className="p-2">
      <ImageCard
        image={image}
        onSelect={onImageSelect}
        onGenerateDescription={onGenerateDescription}
        isSelected={selectedImageId === image.id}
        showActions={true}
      />
    </div>
  );
};

export const SearchResults: React.FC<SearchResultsProps> = ({
  images,
  isLoading,
  hasMore,
  onLoadMore,
  onImageSelect,
  onGenerateDescription,
  selectedImageId,
  className = '',
}) => {
  const { width: windowWidth, height: windowHeight } = useWindowSize();

  // Calculate grid dimensions based on window size
  const { columnsPerRow, columnWidth, rowHeight, containerHeight } = useMemo(() => {
    const containerWidth = Math.min(windowWidth - 64, 1200); // Max width with padding
    const minColumnWidth = 280;
    const maxColumns = 4;
    
    const calculatedColumns = Math.floor(containerWidth / minColumnWidth);
    const columns = Math.min(Math.max(calculatedColumns, 1), maxColumns);
    
    const width = containerWidth / columns;
    const height = 320; // Fixed height for consistency
    const gridHeight = Math.min(windowHeight - 200, 800); // Max height with header/footer space
    
    return {
      columnsPerRow: columns,
      columnWidth: width,
      rowHeight: height,
      containerHeight: gridHeight,
    };
  }, [windowWidth, windowHeight]);

  const rowCount = Math.ceil(images.length / columnsPerRow);
  
  // Add extra rows for loading if needed
  const totalRowCount = hasMore ? rowCount + 1 : rowCount;

  // Check if item is loaded for infinite loading
  const isItemLoaded = useCallback(
    (index: number) => {
      const imageIndex = Math.floor(index / columnsPerRow) * columnsPerRow;
      return imageIndex < images.length;
    },
    [images.length, columnsPerRow]
  );

  // Load more items when scrolling
  const loadMoreItems = useCallback(
    async (startIndex: number, stopIndex: number) => {
      if (hasMore && !isLoading) {
        onLoadMore();
      }
    },
    [hasMore, isLoading, onLoadMore]
  );

  // Show empty state if no results and not loading
  if (!isLoading && images.length === 0) {
    return (
      <EmptyState
        title="No images found"
        description="Try searching with different keywords or check your spelling."
        actionText="Try Random Images"
        onAction={() => onLoadMore()}
      />
    );
  }

  // Show initial loading state
  if (isLoading && images.length === 0) {
    return (
      <div className={`grid gap-4 ${className}`}>
        {Array.from({ length: 12 }).map((_, i) => (
          <LoadingSkeleton
            key={i}
            className="w-full aspect-square rounded-lg"
          />
        ))}
      </div>
    );
  }

  const itemData = {
    images,
    columnsPerRow,
    onImageSelect,
    onGenerateDescription,
    selectedImageId,
    isLoading,
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Results count */}
      <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
        {images.length} {images.length === 1 ? 'image' : 'images'} found
        {hasMore && ' (scroll for more)'}
      </div>

      {/* Virtualized grid */}
      <div className="w-full">
        <InfiniteLoader
          isItemLoaded={isItemLoaded}
          itemCount={totalRowCount * columnsPerRow}
          loadMoreItems={loadMoreItems}
          threshold={5} // Load more when 5 items from the end
        >
          {({ onItemsRendered, ref }) => (
            <Grid
              ref={ref}
              className="focus:outline-none"
              columnCount={columnsPerRow}
              columnWidth={columnWidth}
              height={containerHeight}
              rowCount={totalRowCount}
              rowHeight={rowHeight}
              width={windowWidth - 32} // Account for padding
              itemData={itemData}
              onItemsRendered={({
                visibleColumnStartIndex,
                visibleColumnStopIndex,
                visibleRowStartIndex,
                visibleRowStopIndex,
              }) => {
                onItemsRendered({
                  overscanStartIndex: visibleRowStartIndex * columnsPerRow + visibleColumnStartIndex,
                  overscanStopIndex: visibleRowStopIndex * columnsPerRow + visibleColumnStopIndex,
                  visibleStartIndex: visibleRowStartIndex * columnsPerRow + visibleColumnStartIndex,
                  visibleStopIndex: visibleRowStopIndex * columnsPerRow + visibleColumnStopIndex,
                });
              }}
            >
              {GridItem}
            </Grid>
          )}
        </InfiniteLoader>
      </div>

      {/* Loading more indicator */}
      {isLoading && images.length > 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-600 border-t-transparent" />
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading more images...</span>
        </div>
      )}
    </div>
  );
};