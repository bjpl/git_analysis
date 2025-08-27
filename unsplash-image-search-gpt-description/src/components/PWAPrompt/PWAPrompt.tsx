import React, { useState, useEffect } from 'react';
import { XMarkIcon, DevicePhoneMobileIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline';
import { Button } from '../Shared/Button/Button';
import { useAppStore } from '../../stores/appStore';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export const PWAPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const { settings } = useAppStore();

  useEffect(() => {
    // Check if app is already installed
    const checkIfInstalled = () => {
      if (window.matchMedia('(display-mode: standalone)').matches || 
          (window.navigator as any).standalone === true) {
        setIsInstalled(true);
      }
    };

    checkIfInstalled();

    // Listen for PWA install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      
      // Show prompt after a delay if user hasn't dismissed it before
      const hasSeenPrompt = localStorage.getItem('pwa-prompt-dismissed');
      if (!hasSeenPrompt && !isInstalled) {
        setTimeout(() => setShowPrompt(true), 3000);
      }
    };

    // Listen for app installed
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
      localStorage.removeItem('pwa-prompt-dismissed');
    };

    // Listen for service worker updates
    const handleServiceWorkerUpdate = () => {
      setUpdateAvailable(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Check for service worker updates
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', handleServiceWorkerUpdate);
      
      // Check for waiting service worker
      navigator.serviceWorker.getRegistration().then(registration => {
        if (registration?.waiting) {
          setUpdateAvailable(true);
        }
      });
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.removeEventListener('controllerchange', handleServiceWorkerUpdate);
      }
    };
  }, [isInstalled]);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    try {
      await deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
        localStorage.setItem('pwa-prompt-dismissed', 'true');
      }
    } catch (error) {
      console.error('Error showing install prompt:', error);
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-prompt-dismissed', 'true');
  };

  const handleUpdate = async () => {
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration?.waiting) {
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        setUpdateAvailable(false);
        // Refresh the page to use new service worker
        window.location.reload();
      }
    }
  };

  // Don't show prompts if user has disabled notifications
  if (!settings.notifications) {
    return null;
  }

  // Update available prompt (higher priority)
  if (updateAvailable) {
    return (
      <div className="fixed bottom-4 left-4 right-4 z-50 max-w-sm mx-auto">
        <div className="bg-indigo-600 dark:bg-indigo-700 text-white p-4 rounded-lg shadow-lg border">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center">
                <ComputerDesktopIcon className="w-5 h-5" />
              </div>
            </div>
            
            <div className="flex-1">
              <h3 className="text-sm font-medium">Update Available</h3>
              <p className="text-sm opacity-90 mt-1">
                A new version of VocabLens is ready with bug fixes and improvements.
              </p>
              
              <div className="flex space-x-2 mt-3">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={handleUpdate}
                  className="bg-white/20 text-white hover:bg-white/30 border-white/30"
                >
                  Update Now
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setUpdateAvailable(false)}
                  className="text-white/80 hover:text-white hover:bg-white/10"
                >
                  Later
                </Button>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setUpdateAvailable(false)}
              className="text-white/80 hover:text-white hover:bg-white/10 p-1"
            >
              <XMarkIcon className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Install prompt
  if (showPrompt && deferredPrompt && !isInstalled) {
    return (
      <div className="fixed bottom-4 left-4 right-4 z-50 max-w-sm mx-auto">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-indigo-100 dark:bg-indigo-900/50 rounded-full flex items-center justify-center">
                <DevicePhoneMobileIcon className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              </div>
            </div>
            
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Install VocabLens
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Add VocabLens to your home screen for faster access and offline use.
              </p>
              
              <div className="flex space-x-2 mt-3">
                <Button
                  size="sm"
                  onClick={handleInstallClick}
                >
                  Install
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleDismiss}
                >
                  Not now
                </Button>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDismiss}
              className="p-1"
            >
              <XMarkIcon className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};