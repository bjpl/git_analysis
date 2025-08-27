import React from 'react';
import { MagnifyingGlassIcon, PhotoIcon } from '@heroicons/react/24/outline';
import { Button } from '../Button/Button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  icon?: 'search' | 'photo' | React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionText,
  onAction,
  icon = 'search',
  className = '',
}) => {
  const renderIcon = () => {
    if (React.isValidElement(icon)) {
      return icon;
    }

    const iconClasses = 'w-12 h-12 text-gray-400 dark:text-gray-500';
    
    switch (icon) {
      case 'search':
        return <MagnifyingGlassIcon className={iconClasses} />;
      case 'photo':
        return <PhotoIcon className={iconClasses} />;
      default:
        return <MagnifyingGlassIcon className={iconClasses} />;
    }
  };

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
      <div className="mb-4">
        {renderIcon()}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
        {title}
      </h3>
      
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        {description}
      </p>
      
      {actionText && onAction && (
        <Button onClick={onAction} variant="primary">
          {actionText}
        </Button>
      )}
    </div>
  );
};