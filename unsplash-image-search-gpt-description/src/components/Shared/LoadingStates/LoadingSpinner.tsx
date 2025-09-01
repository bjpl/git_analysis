import React from 'react';
import { cn } from '../../../utils/cn';

export interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
  label?: string;
  fullScreen?: boolean;
}

const sizeClasses = {
  xs: 'h-3 w-3 border-[1.5px]',
  sm: 'h-4 w-4 border-[1.5px]',
  md: 'h-6 w-6 border-2',
  lg: 'h-8 w-8 border-2',
  xl: 'h-12 w-12 border-[3px]',
};

const variantClasses = {
  primary: 'border-primary-600 border-t-transparent dark:border-primary-400 dark:border-t-transparent',
  secondary: 'border-gray-600 border-t-transparent dark:border-gray-400 dark:border-t-transparent',
  white: 'border-white border-t-transparent',
  gray: 'border-gray-400 border-t-transparent dark:border-gray-500 dark:border-t-transparent',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  className,
  label,
  fullScreen = false,
}) => {
  const spinner = (
    <div
      className={cn(
        'animate-spin rounded-full',
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      role="status"
      aria-label={label || 'Loading'}
      data-testid="loading-spinner"
    />
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="flex flex-col items-center space-y-4">
          <div
            className={cn(
              'animate-spin rounded-full',
              sizeClasses.xl,
              variantClasses[variant]
            )}
            role="status"
            aria-label={label || 'Loading'}
          />
          {label && (
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
              {label}
            </p>
          )}
        </div>
      </div>
    );
  }

  if (label) {
    return (
      <div className="flex items-center space-x-2">
        {spinner}
        <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      </div>
    );
  }

  return spinner;
};

// Pre-configured spinner variants for common use cases
export const PrimarySpinner: React.FC<Omit<LoadingSpinnerProps, 'variant'>> = (props) => (
  <LoadingSpinner {...props} variant="primary" />
);

export const SecondarySpinner: React.FC<Omit<LoadingSpinnerProps, 'variant'>> = (props) => (
  <LoadingSpinner {...props} variant="secondary" />
);

export const WhiteSpinner: React.FC<Omit<LoadingSpinnerProps, 'variant'>> = (props) => (
  <LoadingSpinner {...props} variant="white" />
);

export const GraySpinner: React.FC<Omit<LoadingSpinnerProps, 'variant'>> = (props) => (
  <LoadingSpinner {...props} variant="gray" />
);

// Loading states for common UI patterns
export const ButtonSpinner: React.FC<{ className?: string }> = ({ className }) => (
  <LoadingSpinner size="sm" variant="white" className={className} />
);

export const CardSpinner: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('flex justify-center items-center p-8', className)}>
    <LoadingSpinner size="lg" variant="primary" label="Loading..." />
  </div>
);

export const FullPageSpinner: React.FC<{ label?: string }> = ({ label = 'Loading...' }) => (
  <LoadingSpinner fullScreen label={label} variant="primary" />
);

export default LoadingSpinner;