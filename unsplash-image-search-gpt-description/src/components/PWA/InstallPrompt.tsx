import React, { useState } from 'react';
import { cn } from '../../utils/cn';
import { usePWA } from './PWAManager';
import { Button } from '../Shared/Button/Button';
import { useLocalStorageBoolean } from '../../hooks/useLocalStorage';
import {
  ArrowDownTrayIcon,
  XMarkIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
} from '@heroicons/react/24/outline';

interface InstallPromptProps {
  onInstallSuccess?: () => void;
  onDismiss?: () => void;
  className?: string;
}

/**
 * InstallPrompt component that shows PWA installation banner
 * Respects user dismissal preferences and shows platform-specific instructions
 */
export function InstallPrompt({ onInstallSuccess, onDismiss, className }: InstallPromptProps) {
  const { state, actions } = usePWA();
  const [isInstalling, setIsInstalling] = useState(false);
  const [showManualInstructions, setShowManualInstructions] = useState(false);
  const [isDismissed, setIsDismissed] = useLocalStorageBoolean('pwa-install-dismissed', false);
  const [dismissedCount, setDismissedCount] = useLocalStorageBoolean('pwa-install-dismiss-count', 0);

  // Don't show if dismissed too many times or not installable
  if (isDismissed || dismissedCount >= 3 || !state.isInstallable || state.isInstalled) {
    return null;
  }

  const handleInstall = async () => {
    if (!state.installPromptEvent) {
      setShowManualInstructions(true);
      return;
    }

    setIsInstalling(true);
    try {
      await actions.installApp();
      setIsDismissed(true);
      onInstallSuccess?.();
    } catch (error) {
      console.error('Installation failed:', error);
      setShowManualInstructions(true);
    } finally {
      setIsInstalling(false);
    }
  };

  const handleDismiss = () => {
    setDismissedCount(dismissedCount + 1);
    setIsDismissed(true);
    actions.dismissInstallPrompt();
    onDismiss?.();
  };

  const handleNotNow = () => {
    setDismissedCount(dismissedCount + 1);
  };

  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  if (showManualInstructions) {
    return (
      <div className={cn(
        'fixed bottom-4 left-4 right-4 z-50 max-w-sm mx-auto',
        'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700',
        'rounded-lg shadow-lg p-4 animate-slide-up',
        className
      )}>
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            Install VocabLens
          </h3>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setShowManualInstructions(false)}
            aria-label="Close installation instructions"
          >
            <XMarkIcon className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
          {isIOS ? (
            <div className="space-y-2">
              <p className="font-medium text-gray-900 dark:text-white">On iOS Safari:</p>
              <ol className="list-decimal list-inside space-y-1 text-xs">
                <li>Tap the Share button (square with arrow up)</li>
                <li>Scroll down and tap "Add to Home Screen"</li>
                <li>Tap "Add" to confirm</li>
              </ol>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="font-medium text-gray-900 dark:text-white">To install:</p>
              <ol className="list-decimal list-inside space-y-1 text-xs">
                <li>Look for the install icon in your browser's address bar</li>
                <li>Click the install button or "Add to Home Screen"</li>
                <li>Follow the prompts to install</li>
              </ol>
            </div>
          )}
        </div>
        
        <div className="mt-4 flex gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowManualInstructions(false)}
            className="flex-1"
          >
            Got it
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn(
      'fixed bottom-4 left-4 right-4 z-50 max-w-sm mx-auto',
      'bg-gradient-to-r from-primary-500 to-primary-600 text-white',
      'rounded-lg shadow-lg p-4 animate-slide-up',
      className
    )}>
      <div className="flex items-start gap-3">
        {isMobile ? (
          <DevicePhoneMobileIcon className="h-8 w-8 flex-shrink-0 mt-0.5" />
        ) : (
          <ComputerDesktopIcon className="h-8 w-8 flex-shrink-0 mt-0.5" />
        )}
        
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold mb-1">
            Install VocabLens
          </h3>
          <p className="text-xs opacity-90 mb-3">
            Get instant access, work offline, and enjoy a native app experience.
          </p>
          
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleInstall}
              disabled={isInstalling}
              loading={isInstalling}
              loadingText="Installing..."
              leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
              className="bg-white/20 hover:bg-white/30 text-white border-white/30 flex-1"
            >
              Install
            </Button>
          </div>
        </div>
        
        <div className="flex flex-col gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleDismiss}
            className="text-white/80 hover:text-white hover:bg-white/20 -mr-1"
            aria-label="Dismiss install prompt permanently"
          >
            <XMarkIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="mt-3 flex justify-center">
        <Button
          variant="link"
          size="xs"
          onClick={handleNotNow}
          className="text-white/80 hover:text-white text-xs"
        >
          Not now
        </Button>
      </div>
    </div>
  );
}

/**
 * Compact install button for header or other locations
 */
interface InstallButtonProps {
  variant?: 'button' | 'icon';
  className?: string;
}

export function InstallButton({ variant = 'button', className }: InstallButtonProps) {
  const { state, actions } = usePWA();
  const [isInstalling, setIsInstalling] = useState(false);

  if (!state.isInstallable || state.isInstalled) {
    return null;
  }

  const handleInstall = async () => {
    if (!state.installPromptEvent) return;

    setIsInstalling(true);
    try {
      await actions.installApp();
    } catch (error) {
      console.error('Installation failed:', error);
    } finally {
      setIsInstalling(false);
    }
  };

  if (variant === 'icon') {
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={handleInstall}
        disabled={isInstalling}
        className={cn('text-gray-600 dark:text-gray-400', className)}
        aria-label="Install app"
        title="Install VocabLens"
      >
        {isInstalling ? (
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : (
          <ArrowDownTrayIcon className="h-5 w-5" />
        )}
      </Button>
    );
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleInstall}
      disabled={isInstalling}
      loading={isInstalling}
      loadingText="Installing..."
      leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
      className={className}
    >
      Install App
    </Button>
  );
}