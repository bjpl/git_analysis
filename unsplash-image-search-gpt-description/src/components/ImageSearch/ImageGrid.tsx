import React, { useMemo, useCallback } from 'react';
import { FixedSizeGrid as Grid } from 'react-window';
import { useWindowSize } from '../../hooks/useWindowSize';
import { Image } from '../../types';
import { ImageCard } from './ImageCard';
import { LoadingSpinner } from '../Shared/LoadingStates/LoadingSpinner';
import { LoadingSkeleton } from '../Shared/LoadingStates/LoadingSkeleton';
import { EmptyState } from '../Shared/EmptyState/EmptyState';
import { cn } from '../../utils/cn';

export interface ImageGridProps {
  images: Image[];
  isLoading?: boolean;
  onImageSelect: (image: Image) => void;
  onGenerateDescription: (image: Image) => void;
  selectedImageId?: string;
  className?: string;
  showActions?: boolean;
  gridGap?: number;
  minColumnWidth?: number;
  maxColumns?: number;
  aspectRatio?: 'square' | 'portrait' | 'landscape' | 'auto';
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
    showActions: boolean;
    isLoading: boolean;
    gridGap: number;
  };
}

const GridItem: React.FC<GridItemProps> = ({ 
  columnIndex, 
  rowIndex, 
  style, 
  data 
}) => {
  const { 
    images, 
    columnsPerRow, 
    onImageSelect, 
    onGenerateDescription, 
    selectedImageId, 
    showActions, 
    isLoading,
    gridGap
  } = data;
  
  const index = rowIndex * columnsPerRow + columnIndex;
  const image = images[index];

  const itemStyle = {
    ...style,
    left: Number(style.left) + gridGap / 2,
    top: Number(style.top) + gridGap / 2,
    width: Number(style.width) - gridGap,
    height: Number(style.height) - gridGap,
  };

  if (!image) {
    return (
      <div style={itemStyle}>
        {isLoading && index < images.length + 12 ? (
          <LoadingSkeleton className="w-full h-full rounded-lg" />
        ) : null}
      </div>
    );
  }

  return (
    <div style={itemStyle}>
      <ImageCard
        image={image}
        onSelect={onImageSelect}
        onGenerateDescription={onGenerateDescription}
        isSelected={selectedImageId === image.id}
        showActions={showActions}
      />
    </div>
  );
};

export const ImageGrid: React.FC<ImageGridProps> = ({
  images,
  isLoading = false,
  onImageSelect,
  onGenerateDescription,
  selectedImageId,
  className,
  showActions = true,
  gridGap = 16,
  minColumnWidth = 280,
  maxColumns = 4,
  aspectRatio = 'square',
}) => {
  const { width: windowWidth, height: windowHeight } = useWindowSize();

  // Calculate responsive grid dimensions
  const gridConfig = useMemo(() => {
    // Account for padding and potential scrollbar
    const availableWidth = Math.min(windowWidth - 64, 1200);
    const availableHeight = windowHeight - 200; // Account for header/footer
    
    // Calculate columns based on min width
    const calculatedColumns = Math.floor((availableWidth + gridGap) / (minColumnWidth + gridGap));
    const columns = Math.min(Math.max(calculatedColumns, 1), maxColumns);
    
    // Calculate actual column width
    const columnWidth = (availableWidth - (gridGap * (columns - 1))) / columns;
    
    // Calculate row height based on aspect ratio
    let rowHeight: number;
    switch (aspectRatio) {
      case 'portrait':
        rowHeight = columnWidth * 1.25; // 4:5 ratio
        break;
      case 'landscape':
        rowHeight = columnWidth * 0.75; // 4:3 ratio
        break;
      case 'auto':
        rowHeight = columnWidth * 0.8; // Variable height
        break;
      case 'square':
      default:
        rowHeight = columnWidth;
        break;
    }
    
    const rowCount = Math.ceil(images.length / columns);
    const gridHeight = Math.min(availableHeight, (rowHeight + gridGap) * Math.min(rowCount, 6) - gridGap);
    
    return {
      columns,
      columnWidth,
      rowHeight,
      rowCount,
      gridHeight,
      containerWidth: availableWidth,
    };
  }, [windowWidth, windowHeight, images.length, gridGap, minColumnWidth, maxColumns, aspectRatio]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (!selectedImageId || images.length === 0) return;
    
    const currentIndex = images.findIndex(img => img.id === selectedImageId);
    if (currentIndex === -1) return;
    
    let newIndex = currentIndex;
    
    switch (event.key) {
      case 'ArrowLeft':
        newIndex = Math.max(0, currentIndex - 1);
        break;
      case 'ArrowRight':
        newIndex = Math.min(images.length - 1, currentIndex + 1);
        break;
      case 'ArrowUp':
        newIndex = Math.max(0, currentIndex - gridConfig.columns);
        break;
      case 'ArrowDown':
        newIndex = Math.min(images.length - 1, currentIndex + gridConfig.columns);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        onGenerateDescription(images[currentIndex]);
        return;
      default:
        return;
    }
    
    if (newIndex !== currentIndex) {
      event.preventDefault();
      onImageSelect(images[newIndex]);
    }
  }, [selectedImageId, images, gridConfig.columns, onImageSelect, onGenerateDescription]);

  // Show empty state when no images and not loading
  if (!isLoading && images.length === 0) {
    return (
      <div className={cn('w-full', className)}>
        <EmptyState
          title="No images found"
          description="Try searching with different keywords or browse popular categories."
          actionText="Browse Categories"
          icon="🖼️"
        />
      </div>
    );
  }

  // Show initial loading state
  if (isLoading && images.length === 0) {
    return (
      <div className={cn('w-full', className)}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <LoadingSkeleton
              key={i}
              className="aspect-square rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  const itemData = {
    images,
    columnsPerRow: gridConfig.columns,
    onImageSelect,
    onGenerateDescription,
    selectedImageId,
    showActions,
    isLoading,
    gridGap,
  };

  return (
    <div 
      className={cn('w-full focus:outline-none', className)}
      tabIndex={0}
      onKeyDown={handleKeyDown}
      role="grid"
      aria-label="Image grid"
    >
      {/* Grid header with count */}
      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {images.length === 0 ? '0 images' : (
            <>
              {images.length.toLocaleString()}{' '}
              {images.length === 1 ? 'image' : 'images'} found
            </>
          )}
        </div>
        
        {isLoading && images.length > 0 && (
          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <LoadingSpinner size="xs" variant="gray" />
            <span>Loading more...</span>
          </div>
        )}
      </div>

      {/* Virtualized grid */}
      <div className="relative" style={{ height: gridConfig.gridHeight }}>
        <Grid
          className="focus:outline-none scrollbar-thin scrollbar-track-gray-100 dark:scrollbar-track-gray-800 scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600"
          columnCount={gridConfig.columns}
          columnWidth={gridConfig.columnWidth}
          height={gridConfig.gridHeight}
          rowCount={gridConfig.rowCount}
          rowHeight={gridConfig.rowHeight}
          width={gridConfig.containerWidth}
          itemData={itemData}
          overscanRowCount={2}
          overscanColumnCount={1}
        >
          {GridItem}
        </Grid>
      </div>
      
      {/* Keyboard navigation hint */}
      {selectedImageId && (
        <div className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
          Use arrow keys to navigate, Enter/Space to generate description
        </div>
      )}
    </div>
  );
};

export default ImageGrid;