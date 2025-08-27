import React, { useState, memo } from 'react';
import { 
  HeartIcon, 
  ArrowDownTrayIcon, 
  SparklesIcon,
  EyeIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolid } from '@heroicons/react/24/solid';
import { Image, ImageCardProps } from '../../types';
import { Button } from '../Shared/Button/Button';
import { useTrackDownload } from '../../hooks/useImageSearch';
import toast from 'react-hot-toast';

export const ImageCard: React.FC<ImageCardProps> = memo(({
  image,
  onSelect,
  onGenerateDescription,
  isSelected = false,
  showActions = true,
}) => {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isImageError, setIsImageError] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const trackDownload = useTrackDownload();

  const handleImageLoad = () => {
    setIsImageLoaded(true);
    setIsImageError(false);
  };

  const handleImageError = () => {
    setIsImageLoaded(false);
    setIsImageError(true);
  };

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLiked(!isLiked);
    toast.success(isLiked ? 'Removed from favorites' : 'Added to favorites');
  };

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsDownloading(true);

    try {
      // Track download with Unsplash
      await trackDownload(image);

      // Create download link
      const link = document.createElement('a');
      link.href = image.urls.full;
      link.download = `unsplash-${image.id}.jpg`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success('Download started');
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Failed to download image');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleGenerateDescription = (e: React.MouseEvent) => {
    e.stopPropagation();
    onGenerateDescription(image);
  };

  const handleViewImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect(image);
  };

  // Format user display name
  const userDisplayName = image.user?.name || image.user?.username || 'Unknown';
  const imageAlt = image.alt_description || image.description || `Photo by ${userDisplayName}`;

  return (
    <div
      className={`group relative bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden 
                  transition-all duration-200 hover:shadow-xl hover:scale-[1.02] cursor-pointer
                  ${isSelected ? 'ring-2 ring-indigo-500 shadow-lg' : ''}
                  ${!isImageLoaded && !isImageError ? 'animate-pulse' : ''}`}
      onClick={() => onSelect(image)}
      role="button"
      tabIndex={0}
      aria-label={`View image: ${imageAlt}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(image);
        }
      }}
    >
      {/* Image Container */}
      <div className="relative aspect-square overflow-hidden bg-gray-200 dark:bg-gray-700">
        {!isImageError ? (
          <img
            src={image.urls.small}
            alt={imageAlt}
            className={`w-full h-full object-cover transition-opacity duration-300
                       ${isImageLoaded ? 'opacity-100' : 'opacity-0'}`}
            onLoad={handleImageLoad}
            onError={handleImageError}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-100 dark:bg-gray-700">
            <div className="text-center text-gray-400 dark:text-gray-500">
              <UserIcon className="w-12 h-12 mx-auto mb-2" />
              <p className="text-sm">Image unavailable</p>
            </div>
          </div>
        )}

        {/* Loading skeleton */}
        {!isImageLoaded && !isImageError && (
          <div className="absolute inset-0 bg-gray-200 dark:bg-gray-700 animate-pulse" />
        )}

        {/* Overlay actions - show on hover */}
        {showActions && !isImageError && (
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 
                         transition-all duration-200 flex items-center justify-center">
            <div className="opacity-0 group-hover:opacity-100 transform scale-90 group-hover:scale-100 
                           transition-all duration-200 flex space-x-2">
              
              {/* View button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleViewImage}
                className="bg-white/90 text-gray-900 hover:bg-white"
                aria-label="View full image"
              >
                <EyeIcon className="w-4 h-4" />
              </Button>

              {/* Generate description button */}
              <Button
                variant="primary"
                size="sm"
                onClick={handleGenerateDescription}
                className="bg-indigo-600/90 hover:bg-indigo-700"
                aria-label="Generate AI description"
              >
                <SparklesIcon className="w-4 h-4" />
              </Button>

              {/* Download button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleDownload}
                disabled={isDownloading}
                className="bg-white/90 text-gray-900 hover:bg-white disabled:opacity-50"
                aria-label="Download image"
              >
                {isDownloading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-900 border-t-transparent" />
                ) : (
                  <ArrowDownTrayIcon className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Like button - top right */}
        {showActions && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLike}
            className="absolute top-2 right-2 p-1.5 bg-white/80 hover:bg-white/90 backdrop-blur-sm 
                      opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            aria-label={isLiked ? 'Remove from favorites' : 'Add to favorites'}
          >
            {isLiked ? (
              <HeartSolid className="w-4 h-4 text-red-500" />
            ) : (
              <HeartIcon className="w-4 h-4 text-gray-600" />
            )}
          </Button>
        )}
      </div>

      {/* Image Info */}
      <div className="p-3">
        {/* Description */}
        {(image.description || image.alt_description) && (
          <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mb-2">
            {image.description || image.alt_description}
          </p>
        )}

        {/* User info */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <img
              src={image.user?.profile_image?.small || '/default-avatar.png'}
              alt={`${userDisplayName}'s avatar`}
              className="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = '/default-avatar.png';
              }}
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200 truncate">
              {userDisplayName}
            </span>
          </div>

          {/* Image dimensions */}
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {image.width}×{image.height}
          </span>
        </div>

        {/* Tags */}
        {image.tags && image.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {image.tags.slice(0, 3).map((tag, index) => (
              <span
                key={`${tag.title}-${index}`}
                className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 
                         text-gray-600 dark:text-gray-300 rounded-full truncate max-w-20"
                title={tag.title}
              >
                {tag.title}
              </span>
            ))}
            {image.tags.length > 3 && (
              <span className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 
                             text-gray-600 dark:text-gray-300 rounded-full">
                +{image.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
});