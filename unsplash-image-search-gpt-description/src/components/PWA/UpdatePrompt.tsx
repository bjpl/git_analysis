import React, { useState, useEffect } from 'react';
import { cn } from '../../utils/cn';
import { usePWA } from './PWAManager';
import { Button } from '../Shared/Button/Button';
import { useLocalStorageBoolean } from '../../hooks/useLocalStorage';
import {
  ArrowPathIcon,
  XMarkIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface UpdatePromptProps {
  onUpdate?: () => void;
  onDismiss?: () => void;
  isUpdating?: boolean;
  className?: string;
}

/**
 * UpdatePrompt component that notifies users of available app updates
 * Handles service worker updates with user control over when to apply them
 */
export function UpdatePrompt({ onUpdate, onDismiss, isUpdating: externalIsUpdating, className }: UpdatePromptProps) {
  const { state, actions } = usePWA();
  const [isVisible, setIsVisible] = useState(false);
  const [hasBeenDismissed, setHasBeenDismissed] = useLocalStorageBoolean(
    'update-prompt-dismissed',
    false
  );
  const [dismissedVersion, setDismissedVersion] = useState<string | null>(null);
  
  const isUpdating = externalIsUpdating ?? state.isUpdating;

  // Show prompt when update is available and not dismissed
  useEffect(() => {
    if (state.updateAvailable && !hasBeenDismissed) {
      setIsVisible(true);
    }
  }, [state.updateAvailable, hasBeenDismissed]);

  // Reset dismissed state when a new update is available
  useEffect(() => {
    if (state.updateAvailable) {
      const currentVersion = new Date().toISOString(); // Simplified versioning
      if (dismissedVersion !== currentVersion) {
        setHasBeenDismissed(false);
        setDismissedVersion(currentVersion);
      }
    }
  }, [state.updateAvailable, dismissedVersion]);

  const handleUpdate = async () => {
    try {
      if (onUpdate) {
        onUpdate();
      } else {
        await actions.updateApp();
      }
    } catch (error) {
      console.error('Failed to update app:', error);
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
    setHasBeenDismissed(true);
    onDismiss?.();
  };

  const handleLater = () => {
    setIsVisible(false);
    // Don't mark as permanently dismissed, so it can show again later
  };

  if (!isVisible || !state.updateAvailable) {
    return null;
  }

  return (
    <div className={cn(
      'fixed top-4 right-4 z-50 max-w-sm',
      'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700',
      'rounded-lg shadow-lg animate-slide-down',
      className
    )}>
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Update Available
            </h3>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleDismiss}
            className="-mr-1"
            aria-label="Dismiss update notification"
          >
            <XMarkIcon className="h-4 w-4" />
          </Button>
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          A new version of VocabLens is available with improved features and bug fixes.
        </p>
        
        <div className="flex gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleUpdate}
            disabled={isUpdating}
            loading={isUpdating}
            loadingText="Updating..."
            leftIcon={<ArrowPathIcon className="h-4 w-4" />}
            className="flex-1"
          >
            Update Now
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLater}
            disabled={isUpdating}
          >
            Later
          </Button>
        </div>
        
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            The app will refresh automatically after updating.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Critical update prompt for security or breaking changes
 */
interface CriticalUpdatePromptProps {
  isVisible: boolean;
  onUpdate: () => void;
  updateDetails?: string;
  className?: string;
}

export function CriticalUpdatePrompt({
  isVisible,
  onUpdate,
  updateDetails = 'A critical security update is required.',
  className,
}: CriticalUpdatePromptProps) {
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdate = async () => {
    setIsUpdating(true);
    try {
      await onUpdate();
    } catch (error) {
      console.error('Critical update failed:', error);
      setIsUpdating(false);
    }
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className={cn(
        'w-full max-w-md mx-4 bg-white dark:bg-gray-900',
        'border border-red-200 dark:border-red-800 rounded-lg shadow-xl',
        className
      )}>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600 dark:text-red-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Critical Update Required
            </h3>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            {updateDetails}
          </p>
          
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-6">
            <p className="text-xs text-red-700 dark:text-red-300">
              This update is mandatory and contains important security fixes. 
              The app cannot continue without this update.
            </p>
          </div>
          
          <Button
            variant="danger"
            onClick={handleUpdate}
            disabled={isUpdating}
            loading={isUpdating}
            loadingText="Updating..."
            leftIcon={<ArrowPathIcon className="h-4 w-4" />}
            fullWidth
          >
            Update Now
          </Button>
          
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-3">
            The app will restart automatically after the update.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Compact update indicator for status bar or header
 */
interface UpdateIndicatorProps {
  onClick?: () => void;
  className?: string;
}

export function UpdateIndicator({ onClick, className }: UpdateIndicatorProps) {
  const { state, actions } = usePWA();

  if (!state.updateAvailable) {
    return null;
  }

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      actions.updateApp();
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleClick}
      disabled={isUpdating}
      className={cn(
        'text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300',
        className
      )}
      title="Update available - click to update"
    >
      {state.isUpdating ? (
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 animate-spin rounded-full border border-current border-t-transparent" />
          <span className="text-xs">Updating...</span>
        </div>
      ) : (
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 bg-primary-600 dark:bg-primary-400 rounded-full animate-pulse" />
          <span className="text-xs font-medium">Update</span>
        </div>
      )}
    </Button>
  );
}