import React from 'react';
import { cn } from '@/utils/cn';

interface LoadingSkeletonProps {
  className?: string;
  lines?: number;
  variant?: 'rectangular' | 'circular' | 'text' | 'card' | 'image' | 'avatar';
  width?: string;
  height?: string;
}

/**
 * LoadingSkeleton component for showing loading placeholders
 * Supports various shapes and multi-line text placeholders
 */
export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  className = '',
  lines = 1,
  variant = 'rectangular',
  width,
  height,
}) => {
  const baseClasses = 'animate-pulse bg-gray-200 dark:bg-gray-700';
  
  const variantClasses = {
    rectangular: 'rounded-md',
    circular: 'rounded-full',
    text: 'rounded h-4',
    card: 'rounded-lg h-32',
    image: 'rounded-lg aspect-video',
    avatar: 'rounded-full w-10 h-10',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = width;
  if (height) style.height = height;

  if (variant === 'text' && lines > 1) {
    return (
      <div className={className}>
        {Array.from({ length: lines }).map((_, index) => {
          const isLast = index === lines - 1;
          return (
            <div
              key={index}
              className={cn(
                baseClasses,
                variantClasses.text,
                !isLast && 'mb-2',
                isLast && 'w-3/4'
              )}
            />
          );
        })}
      </div>
    );
  }

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        className
      )}
      style={style}
      role="status"
      aria-label="Loading"
    />
  );
};

/**
 * Enhanced LoadingSpinner component with more size options and variants
 */
interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'dots' | 'pulse';
  className?: string;
  color?: 'primary' | 'secondary' | 'white';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'default',
  className = '',
  color = 'primary',
}) => {
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  };

  const colorClasses = {
    primary: 'border-primary-600 border-t-transparent',
    secondary: 'border-gray-600 border-t-transparent',
    white: 'border-white border-t-transparent',
  };

  if (variant === 'dots') {
    return (
      <div className={cn('flex space-x-1', className)} role="status" aria-label="Loading">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={cn(
              'rounded-full bg-primary-600 animate-pulse',
              size === 'xs' && 'w-1 h-1',
              size === 'sm' && 'w-1.5 h-1.5',
              size === 'md' && 'w-2 h-2',
              size === 'lg' && 'w-3 h-3',
              size === 'xl' && 'w-4 h-4'
            )}
            style={{
              animationDelay: `${i * 0.2}s`,
              animationDuration: '1.4s',
            }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'pulse') {
    return (
      <div
        className={cn(
          'rounded-full bg-primary-600 animate-pulse',
          sizeClasses[size],
          className
        )}
        role="status"
        aria-label="Loading"
      />
    );
  }

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      role="status"
      aria-label="Loading"
    />
  );
};

/**
 * Card skeleton for loading states in card layouts
 */
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('p-6 space-y-4', className)}>
      <LoadingSkeleton variant="rectangular" className="h-6 w-3/4" />
      <LoadingSkeleton variant="text" lines={3} />
      <div className="flex justify-between items-center">
        <LoadingSkeleton variant="rectangular" className="h-8 w-20" />
        <LoadingSkeleton variant="circular" className="h-8 w-8" />
      </div>
    </div>
  );
};

/**
 * Image card skeleton for image gallery loading states
 */
export const ImageCardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-3', className)}>
      <LoadingSkeleton variant="image" className="w-full" />
      <div className="space-y-2">
        <LoadingSkeleton variant="text" className="w-full" />
        <LoadingSkeleton variant="text" className="w-2/3" />
      </div>
      <div className="flex items-center space-x-2">
        <LoadingSkeleton variant="avatar" className="w-6 h-6" />
        <LoadingSkeleton variant="text" className="w-24 h-3" />
      </div>
    </div>
  );
};

/**
 * List item skeleton for list loading states
 */
export const ListItemSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('flex items-center space-x-3 py-3', className)}>
      <LoadingSkeleton variant="avatar" />
      <div className="flex-1 space-y-2">
        <LoadingSkeleton variant="text" className="w-full" />
        <LoadingSkeleton variant="text" className="w-3/4" />
      </div>
      <LoadingSkeleton variant="rectangular" className="w-16 h-8" />
    </div>
  );
};

/**
 * Full page loading component
 */
interface PageLoadingProps {
  message?: string;
  className?: string;
}

export const PageLoading: React.FC<PageLoadingProps> = ({
  message = 'Loading...',
  className,
}) => {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center min-h-64 space-y-4',
      className
    )}>
      <LoadingSpinner size="lg" />
      <p className="text-gray-600 dark:text-gray-400 text-center">
        {message}
      </p>
    </div>
  );
};