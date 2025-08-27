import { useState, useEffect } from 'react';

interface UseOfflineReturn {
  isOnline: boolean;
  isOffline: boolean;
  isInstallable: boolean;
  installPrompt: BeforeInstallPromptEvent | null;
  canInstall: boolean;
  install: () => Promise<void>;
}

// PWA Install Prompt Event interface
interface BeforeInstallPromptEvent extends Event {
  platforms: string[];
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
  prompt(): Promise<void>;
}

/**
 * Hook to manage offline status and PWA installation
 * Tracks network connectivity and PWA install state
 */
export function useOffline(): UseOfflineReturn {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    const checkInstalled = () => {
      if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
        setIsInstalled(true);
      } else if ((window.navigator as any).standalone) {
        // iOS Safari
        setIsInstalled(true);
      }
    };

    checkInstalled();

    // Network status listeners
    const handleOnline = () => {
      setIsOnline(true);
      console.log('App is online');
    };

    const handleOffline = () => {
      setIsOnline(false);
      console.log('App is offline');
    };

    // PWA install prompt listener
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      console.log('PWA install prompt available');
      setInstallPrompt(e as BeforeInstallPromptEvent);
    };

    // PWA install success listener
    const handleAppInstalled = () => {
      console.log('PWA was installed');
      setIsInstalled(true);
      setInstallPrompt(null);
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const install = async (): Promise<void> => {
    if (!installPrompt) {
      throw new Error('Install prompt not available');
    }

    try {
      // Show the install prompt
      await installPrompt.prompt();
      
      // Wait for user choice
      const choiceResult = await installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted PWA install');
      } else {
        console.log('User dismissed PWA install');
      }
      
      // Clear the prompt as it can only be used once
      setInstallPrompt(null);
    } catch (error) {
      console.error('Error installing PWA:', error);
      throw error;
    }
  };

  return {
    isOnline,
    isOffline: !isOnline,
    isInstallable: !!installPrompt && !isInstalled,
    installPrompt,
    canInstall: !!installPrompt,
    install,
  };
}

/**
 * Hook to manage offline data synchronization
 * Queues operations while offline and syncs when back online
 */
export function useOfflineSync<T = any>() {
  const [queue, setQueue] = useState<T[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const { isOnline } = useOffline();

  // Add operation to queue
  const enqueue = (operation: T) => {
    setQueue(prev => [...prev, operation]);
  };

  // Process queue when online
  const sync = async (processor: (operations: T[]) => Promise<void>) => {
    if (!isOnline || queue.length === 0 || isSyncing) {
      return;
    }

    setIsSyncing(true);
    try {
      await processor(queue);
      setQueue([]);
      console.log('Offline operations synced successfully');
    } catch (error) {
      console.error('Failed to sync offline operations:', error);
      throw error;
    } finally {
      setIsSyncing(false);
    }
  };

  // Auto-sync when coming back online
  useEffect(() => {
    if (isOnline && queue.length > 0 && !isSyncing) {
      // Auto-sync can be implemented here if needed
      console.log(`${queue.length} operations queued for sync`);
    }
  }, [isOnline, queue.length, isSyncing]);

  return {
    queue,
    queueLength: queue.length,
    isSyncing,
    enqueue,
    sync,
    clearQueue: () => setQueue([]),
  };
}

/**
 * Hook to manage service worker updates
 * Detects and handles service worker updates
 */
export function useServiceWorker() {
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistration()
        .then(reg => {
          if (reg) {
            setRegistration(reg);

            // Check for updates
            const checkForUpdates = () => {
              if (reg.waiting) {
                setIsUpdateAvailable(true);
              }
            };

            reg.addEventListener('updatefound', () => {
              const newWorker = reg.installing;
              if (newWorker) {
                newWorker.addEventListener('statechange', () => {
                  if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    setIsUpdateAvailable(true);
                  }
                });
              }
            });

            checkForUpdates();
          }
        })
        .catch(error => {
          console.error('Service worker registration check failed:', error);
        });
    }
  }, []);

  const updateServiceWorker = async () => {
    if (!registration || !registration.waiting) {
      return;
    }

    setIsUpdating(true);
    
    try {
      // Tell the waiting service worker to skip waiting
      registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      
      // Listen for the controlling service worker to change
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      }, { once: true });
    } catch (error) {
      console.error('Failed to update service worker:', error);
      setIsUpdating(false);
    }
  };

  return {
    isUpdateAvailable,
    isUpdating,
    registration,
    updateServiceWorker,
  };
}