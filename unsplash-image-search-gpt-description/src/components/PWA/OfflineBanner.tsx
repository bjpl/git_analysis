/**
 * Offline Banner Component for VocabLens PWA
 * 
 * Shows users when they're offline and provides information about
 * offline capabilities and sync status.
 */

import React, { useState, useEffect } from 'react';
import { useOfflineSync } from '../../hooks/useOfflineSync';
import { 
  WifiIcon, 
  CloudIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface OfflineBannerProps {
  className?: string;
  showWhenOnline?: boolean;
  showSyncStatus?: boolean;
  autoHide?: boolean;
  autoHideDelay?: number;
}

export function OfflineBanner({
  className = '',
  showWhenOnline = false,
  showSyncStatus = true,
  autoHide = true,
  autoHideDelay = 5000
}: OfflineBannerProps): JSX.Element | null {
  const { syncStatus, networkStatus, syncNow } = useOfflineSync();
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Show banner when offline or when sync is pending
  useEffect(() => {
    const shouldShow = 
      !isDismissed && 
      (!networkStatus.isOnline || 
       (showWhenOnline && syncStatus.pendingCount > 0) ||
       syncStatus.isSyncing ||
       syncStatus.conflicts.length > 0 ||
       syncStatus.errors.length > 0);

    setIsVisible(shouldShow);

    // Auto-hide when online and no issues
    if (autoHide && networkStatus.isOnline && syncStatus.pendingCount === 0 && !syncStatus.isSyncing) {
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, autoHideDelay);
      
      return () => clearTimeout(timer);
    }
  }, [
    networkStatus.isOnline, 
    syncStatus.pendingCount, 
    syncStatus.isSyncing,
    syncStatus.conflicts.length,
    syncStatus.errors.length,
    isDismissed, 
    showWhenOnline, 
    autoHide, 
    autoHideDelay
  ]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
  };

  const handleSync = async () => {
    try {
      await syncNow();
    } catch (error) {
      console.error('Manual sync failed:', error);
    }
  };

  const getStatusIcon = () => {
    if (!networkStatus.isOnline) {
      return <WifiIcon className="h-5 w-5 text-orange-500" />;
    }
    
    if (syncStatus.isSyncing) {
      return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
    }
    
    if (syncStatus.conflicts.length > 0 || syncStatus.errors.length > 0) {
      return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
    }
    
    if (syncStatus.pendingCount > 0) {
      return <CloudIcon className="h-5 w-5 text-yellow-500" />;
    }
    
    return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
  };

  const getStatusMessage = () => {
    if (!networkStatus.isOnline) {
      return {
        title: 'You\'re offline',
        description: 'You can continue learning with cached content. Changes will sync when you\'re back online.',
        variant: 'warning' as const
      };
    }
    
    if (syncStatus.isSyncing) {
      return {
        title: 'Syncing your data...',
        description: `Syncing ${syncStatus.pendingCount} items (${syncStatus.syncProgress}%)`,
        variant: 'info' as const
      };
    }
    
    if (syncStatus.conflicts.length > 0) {
      return {
        title: 'Data conflicts detected',
        description: `${syncStatus.conflicts.length} items need your attention`,
        variant: 'error' as const
      };
    }
    
    if (syncStatus.errors.length > 0) {
      return {
        title: 'Sync errors occurred',
        description: `${syncStatus.errors.length} items failed to sync`,
        variant: 'error' as const
      };
    }
    
    if (syncStatus.pendingCount > 0) {
      return {
        title: 'Pending changes',
        description: `${syncStatus.pendingCount} items waiting to sync`,
        variant: 'warning' as const
      };
    }
    
    return {
      title: 'All synced',
      description: 'Your data is up to date',
      variant: 'success' as const
    };
  };

  const getVariantClasses = (variant: 'success' | 'warning' | 'error' | 'info') => {
    switch (variant) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  if (!isVisible) return null;

  const status = getStatusMessage();

  return (
    <div 
      className={`fixed top-0 left-0 right-0 z-50 transform transition-transform duration-300 ${className}`}
      role="alert"
      aria-live="polite"
    >
      <div className={`border-b ${getVariantClasses(status.variant)} px-4 py-3 shadow-sm`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon()}
            <div className="flex-1">
              <p className="font-medium text-sm">
                {status.title}
              </p>
              <p className="text-xs opacity-90">
                {status.description}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Network Quality Indicator */}
            {networkStatus.isOnline && (
              <div className="flex items-center space-x-1 text-xs">
                <div className="flex space-x-0.5">
                  <div className={`w-1 h-2 rounded-full ${
                    networkStatus.quality === 'excellent' 
                      ? 'bg-green-500' 
                      : networkStatus.quality === 'good' 
                        ? 'bg-yellow-500' 
                        : 'bg-red-500'
                  }`} />
                  <div className={`w-1 h-3 rounded-full ${
                    networkStatus.quality === 'excellent' 
                      ? 'bg-green-500' 
                      : networkStatus.quality === 'good' 
                        ? 'bg-green-500' 
                        : 'bg-gray-300'
                  }`} />
                  <div className={`w-1 h-4 rounded-full ${
                    networkStatus.quality === 'excellent' 
                      ? 'bg-green-500' 
                      : 'bg-gray-300'
                  }`} />
                </div>
                <span className="text-xs opacity-75">
                  {networkStatus.quality}
                </span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              {showSyncStatus && syncStatus.pendingCount > 0 && networkStatus.isOnline && (
                <button
                  onClick={handleSync}
                  disabled={syncStatus.isSyncing}
                  className="text-xs px-2 py-1 rounded bg-white/20 hover:bg-white/30 transition-colors disabled:opacity-50"
                  title="Sync now"
                >
                  {syncStatus.isSyncing ? 'Syncing...' : 'Sync'}
                </button>
              )}

              <button
                onClick={() => setShowDetails(!showDetails)}
                className="text-xs px-2 py-1 rounded bg-white/20 hover:bg-white/30 transition-colors"
                title="Show details"
              >
                Details
              </button>

              <button
                onClick={handleDismiss}
                className="p-1 rounded hover:bg-white/20 transition-colors"
                title="Dismiss"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Sync Progress Bar */}
        {syncStatus.isSyncing && (
          <div className="mt-2">
            <div className="w-full bg-white/20 rounded-full h-1">
              <div
                className="bg-current h-1 rounded-full transition-all duration-300"
                style={{ width: `${syncStatus.syncProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Detailed Status */}
        {showDetails && (
          <div className="mt-3 pt-3 border-t border-current/20">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <div className="font-medium mb-1">Network</div>
                <div className="space-y-1">
                  <div>Status: {networkStatus.isOnline ? 'Online' : 'Offline'}</div>
                  <div>Quality: {networkStatus.quality}</div>
                  <div>Speed: {networkStatus.downlinkSpeed.toFixed(1)} Mbps</div>
                  {networkStatus.rtt && (
                    <div>Latency: {networkStatus.rtt}ms</div>
                  )}
                </div>
              </div>

              <div>
                <div className="font-medium mb-1">Sync Status</div>
                <div className="space-y-1">
                  <div>Pending: {syncStatus.pendingCount}</div>
                  <div>Conflicts: {syncStatus.conflicts.length}</div>
                  <div>Errors: {syncStatus.errors.length}</div>
                  {syncStatus.lastSyncTime && (
                    <div>
                      Last sync: {new Date(syncStatus.lastSyncTime).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <div className="font-medium mb-1">Offline Features</div>
                <div className="space-y-1">
                  <div>✓ View vocabulary</div>
                  <div>✓ Take quizzes</div>
                  <div>✓ Browse cached images</div>
                  <div>✓ Study progress</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default OfflineBanner;