/**
 * PWA Manager Component for VocabLens
 * 
 * Centralized PWA functionality manager that coordinates:
 * - Service Worker registration and updates
 * - Offline synchronization
 * - Push notifications
 * - Storage management
 * - Performance optimization
 * - User experience enhancements
 */

import React, { useEffect, useState, createContext, useContext } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useOfflineSync } from '../../hooks/useOfflineSync';
import { pushNotificationsManager } from '../../lib/push-notifications';
import { storageManager } from '../../lib/storage-manager';
import { performanceOptimizer } from '../../lib/performance-optimizer';
import { OfflineBanner } from './OfflineBanner';
import { InstallPrompt } from './InstallPrompt';
import { UpdatePrompt } from './UpdatePrompt';

export interface PWAState {
  // Installation
  isInstallable: boolean;
  isInstalled: boolean;
  installPromptEvent: any;
  
  // Service Worker
  swRegistration: ServiceWorkerRegistration | null;
  updateAvailable: boolean;
  isUpdating: boolean;
  
  // Offline & Sync
  isOnline: boolean;
  syncStatus: any;
  
  // Notifications
  notificationPermission: NotificationPermission;
  pushSubscribed: boolean;
  
  // Storage
  storageInfo: any;
  
  // Performance
  performanceMetrics: any;
}

export interface PWAActions {
  // Installation
  installApp: () => Promise<void>;
  dismissInstallPrompt: () => void;
  
  // Service Worker
  updateApp: () => Promise<void>;
  skipWaiting: () => Promise<void>;
  
  // Notifications
  requestNotificationPermission: () => Promise<NotificationPermission>;
  subscribeToPushNotifications: () => Promise<void>;
  unsubscribeFromPushNotifications: () => Promise<void>;
  scheduleStudyReminder: (date: Date) => Promise<void>;
  
  // Storage
  clearCache: () => Promise<void>;
  clearAllData: () => Promise<void>;
  getStorageInfo: () => Promise<any>;
  
  // Performance
  optimizeForBattery: () => void;
  getPerformanceMetrics: () => any[];
}

interface PWAContextType {
  state: PWAState;
  actions: PWAActions;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

export const usePWA = (): PWAContextType => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
};

interface PWAManagerProps {
  children: React.ReactNode;
  enableInstallPrompt?: boolean;
  enableUpdatePrompt?: boolean;
  enableOfflineBanner?: boolean;
  enablePerformanceOptimization?: boolean;
  enablePushNotifications?: boolean;
}

/**
 * PWA Manager Provider Component
 */
export function PWAManager({
  children,
  enableInstallPrompt = true,
  enableUpdatePrompt = true,
  enableOfflineBanner = true,
  enablePerformanceOptimization = true,
  enablePushNotifications = true
}: PWAManagerProps): JSX.Element {
  const { user } = useAuth();
  const { syncStatus, networkStatus } = useOfflineSync();

  // PWA State
  const [pwaState, setPWAState] = useState<PWAState>({
    isInstallable: false,
    isInstalled: false,
    installPromptEvent: null,
    swRegistration: null,
    updateAvailable: false,
    isUpdating: false,
    isOnline: navigator.onLine,
    syncStatus,
    notificationPermission: 'default',
    pushSubscribed: false,
    storageInfo: null,
    performanceMetrics: []
  });

  // Initialize PWA functionality
  useEffect(() => {
    initializePWA();
  }, [user?.id]);

  // Update state when sync status changes
  useEffect(() => {
    setPWAState(prev => ({ 
      ...prev, 
      syncStatus, 
      isOnline: networkStatus.isOnline 
    }));
  }, [syncStatus, networkStatus]);

  /**
   * Initialize PWA functionality
   */
  const initializePWA = async (): Promise<void> => {
    try {
      // Register service worker
      await registerServiceWorker();
      
      // Initialize performance optimization
      if (enablePerformanceOptimization) {
        await performanceOptimizer.initialize();
      }
      
      // Initialize storage manager
      if (user?.id) {
        await storageManager.initialize(user.id);
        const storageInfo = await storageManager.getStorageInfo();
        setPWAState(prev => ({ ...prev, storageInfo }));
      }
      
      // Initialize push notifications
      if (enablePushNotifications && user?.id) {
        await initializePushNotifications();
      }
      
      // Set up event listeners
      setupEventListeners();
      
      console.log('PWA initialization completed');
    } catch (error) {
      console.error('PWA initialization failed:', error);
    }
  };

  /**
   * Register service worker
   */
  const registerServiceWorker = async (): Promise<void> => {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service Worker not supported');
      return;
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      
      setPWAState(prev => ({ ...prev, swRegistration: registration }));

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              setPWAState(prev => ({ ...prev, updateAvailable: true }));
            }
          });
        }
      });

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'UPDATE_AVAILABLE') {
          setPWAState(prev => ({ ...prev, updateAvailable: true }));
        }
      });

      console.log('Service Worker registered successfully');
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  };

  /**
   * Initialize push notifications
   */
  const initializePushNotifications = async (): Promise<void> => {
    if (!user?.id) return;

    try {
      const initialized = await pushNotificationsManager.initialize(user.id);
      if (initialized) {
        setPWAState(prev => ({
          ...prev,
          notificationPermission: pushNotificationsManager.getPermissionStatus(),
          pushSubscribed: pushNotificationsManager.isSubscribed()
        }));
      }
    } catch (error) {
      console.error('Push notifications initialization failed:', error);
    }
  };

  /**
   * Setup event listeners
   */
  const setupEventListeners = (): void => {
    // Install prompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      setPWAState(prev => ({
        ...prev,
        isInstallable: true,
        installPromptEvent: e
      }));
    });

    // App installed event
    window.addEventListener('appinstalled', () => {
      setPWAState(prev => ({
        ...prev,
        isInstalled: true,
        isInstallable: false,
        installPromptEvent: null
      }));
      console.log('PWA installed successfully');
    });

    // Online/offline events
    window.addEventListener('online', () => {
      setPWAState(prev => ({ ...prev, isOnline: true }));
    });

    window.addEventListener('offline', () => {
      setPWAState(prev => ({ ...prev, isOnline: false }));
    });

    // Storage events
    storageManager.addStorageCallback((storageInfo) => {
      setPWAState(prev => ({ ...prev, storageInfo }));
    });

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches ||
        (window.navigator as any).standalone) {
      setPWAState(prev => ({ ...prev, isInstalled: true }));
    }
  };

  /**
   * PWA Actions
   */
  const pwaActions: PWAActions = {
    // Installation
    installApp: async () => {
      if (!pwaState.installPromptEvent) return;
      
      try {
        await pwaState.installPromptEvent.prompt();
        const result = await pwaState.installPromptEvent.userChoice;
        
        if (result.outcome === 'accepted') {
          setPWAState(prev => ({
            ...prev,
            isInstalled: true,
            isInstallable: false,
            installPromptEvent: null
          }));
        }
      } catch (error) {
        console.error('App installation failed:', error);
      }
    },

    dismissInstallPrompt: () => {
      setPWAState(prev => ({
        ...prev,
        isInstallable: false,
        installPromptEvent: null
      }));
    },

    // Service Worker
    updateApp: async () => {
      if (!pwaState.swRegistration?.waiting) return;
      
      setPWAState(prev => ({ ...prev, isUpdating: true }));
      
      try {
        pwaState.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
        window.location.reload();
      } catch (error) {
        console.error('App update failed:', error);
        setPWAState(prev => ({ ...prev, isUpdating: false }));
      }
    },

    skipWaiting: async () => {
      if (pwaState.swRegistration?.waiting) {
        pwaState.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      }
    },

    // Notifications
    requestNotificationPermission: async () => {
      try {
        const permission = await pushNotificationsManager.requestPermission();
        setPWAState(prev => ({ 
          ...prev, 
          notificationPermission: permission,
          pushSubscribed: pushNotificationsManager.isSubscribed()
        }));
        return permission;
      } catch (error) {
        console.error('Notification permission request failed:', error);
        return 'denied';
      }
    },

    subscribeToPushNotifications: async () => {
      try {
        await pushNotificationsManager.subscribeToPush();
        setPWAState(prev => ({ ...prev, pushSubscribed: true }));
      } catch (error) {
        console.error('Push notification subscription failed:', error);
      }
    },

    unsubscribeFromPushNotifications: async () => {
      try {
        await pushNotificationsManager.unsubscribe();
        setPWAState(prev => ({ ...prev, pushSubscribed: false }));
      } catch (error) {
        console.error('Push notification unsubscription failed:', error);
      }
    },

    scheduleStudyReminder: async (date: Date) => {
      try {
        await pushNotificationsManager.scheduleStudyReminder({
          scheduledFor: date,
          isRecurring: true,
          recurringPattern: 'daily'
        });
      } catch (error) {
        console.error('Failed to schedule study reminder:', error);
      }
    },

    // Storage
    clearCache: async () => {
      try {
        const result = await storageManager.clearAllData();
        console.log('Cache cleared:', result);
        
        // Update storage info
        const storageInfo = await storageManager.getStorageInfo();
        setPWAState(prev => ({ ...prev, storageInfo }));
      } catch (error) {
        console.error('Failed to clear cache:', error);
      }
    },

    clearAllData: async () => {
      try {
        await storageManager.clearAllData();
        
        // Clear IndexedDB
        await caches.delete('VocabularyAppOfflineDB');
        
        console.log('All data cleared');
      } catch (error) {
        console.error('Failed to clear all data:', error);
      }
    },

    getStorageInfo: async () => {
      try {
        const storageInfo = await storageManager.getStorageInfo();
        setPWAState(prev => ({ ...prev, storageInfo }));
        return storageInfo;
      } catch (error) {
        console.error('Failed to get storage info:', error);
        return null;
      }
    },

    // Performance
    optimizeForBattery: () => {
      performanceOptimizer.optimizeForBattery();
    },

    getPerformanceMetrics: () => {
      return performanceOptimizer.getMetrics();
    }
  };

  const contextValue: PWAContextType = {
    state: pwaState,
    actions: pwaActions
  };

  return (
    <PWAContext.Provider value={contextValue}>
      {children}
      
      {/* PWA UI Components */}
      {enableOfflineBanner && (
        <OfflineBanner 
          showWhenOnline={false}
          autoHide={true}
        />
      )}
      
      {enableInstallPrompt && pwaState.isInstallable && !pwaState.isInstalled && (
        <InstallPrompt
          onInstallSuccess={() => pwaActions.installApp()}
          onDismiss={pwaActions.dismissInstallPrompt}
        />
      )}
      
      {enableUpdatePrompt && pwaState.updateAvailable && (
        <UpdatePrompt
          onUpdate={pwaActions.updateApp}
          onDismiss={() => setPWAState(prev => ({ ...prev, updateAvailable: false }))}
          isUpdating={pwaState.isUpdating}
        />
      )}
    </PWAContext.Provider>
  );
}

/**
 * PWA Status Component - Shows current PWA status
 */
interface PWAStatusProps {
  className?: string;
  detailed?: boolean;
}

export function PWAStatus({ className = '', detailed = false }: PWAStatusProps): JSX.Element {
  const { state } = usePWA();

  return (
    <div className={`pwa-status ${className}`}>
      <div className="flex items-center space-x-4">
        <div className={`status-indicator ${state.isOnline ? 'online' : 'offline'}`}>
          <div className={`w-3 h-3 rounded-full ${state.isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm">{state.isOnline ? 'Online' : 'Offline'}</span>
        </div>
        
        <div className="sync-status">
          <span className="text-sm text-gray-600">
            {state.syncStatus.isSyncing ? 'Syncing...' : 
             state.syncStatus.pendingCount > 0 ? `${state.syncStatus.pendingCount} pending` :
             'Synced'}
          </span>
        </div>
        
        {state.isInstalled && (
          <div className="installed-indicator">
            <span className="text-sm text-green-600">📱 Installed</span>
          </div>
        )}
      </div>
      
      {detailed && (
        <div className="mt-4 space-y-2 text-xs text-gray-500">
          <div>Service Worker: {state.swRegistration ? '✓ Registered' : '✗ Not registered'}</div>
          <div>Notifications: {state.notificationPermission}</div>
          <div>Push: {state.pushSubscribed ? '✓ Subscribed' : '✗ Not subscribed'}</div>
          <div>Storage: {state.storageInfo ? `${(state.storageInfo.percentage || 0).toFixed(1)}% used` : 'Unknown'}</div>
        </div>
      )}
    </div>
  );
}

export default PWAManager;