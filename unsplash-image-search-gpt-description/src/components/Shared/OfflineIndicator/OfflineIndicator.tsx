import React, { useState, useEffect } from 'react';
import { WifiIcon, NoSymbolIcon } from '@heroicons/react/24/outline';
import { useAppStore } from '../../../stores/appStore';
import { useOfflineSync } from '../../../hooks/useOfflineSync';

export const OfflineIndicator: React.FC = () => {
  const { isOnline, setIsOnline } = useAppStore();
  const { queueSize, sync, isSyncing } = useOfflineSync();
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Set initial state
    setIsOnline(navigator.onLine);

    // Listen for network changes
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setIsOnline]);

  // Auto-hide online indicator after 3 seconds
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isOnline && queueSize === 0) {
      timer = setTimeout(() => setShowDetails(false), 3000);
    }
    return () => clearTimeout(timer);
  }, [isOnline, queueSize]);

  // Don't show anything if online and no queue
  if (isOnline && queueSize === 0 && !showDetails) {
    return null;
  }

  return (
    <div className="fixed top-16 left-4 z-40">
      <div
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg shadow-lg border transition-all duration-300 cursor-pointer
          ${isOnline 
            ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-300' 
            : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300'
          }
          ${showDetails ? 'opacity-100' : 'opacity-90 hover:opacity-100'}
        `}
        onClick={() => setShowDetails(!showDetails)}
      >
        {/* Status Icon */}
        <div className="flex-shrink-0">
          {isOnline ? (
            <WifiIcon className="w-4 h-4" />
          ) : (
            <NoSymbolIcon className="w-4 h-4" />
          )}
        </div>

        {/* Status Text */}
        <div className="text-sm font-medium">
          {isOnline ? 'Online' : 'Offline'}
        </div>

        {/* Queue indicator */}
        {queueSize > 0 && (
          <div className={`px-2 py-0.5 rounded-full text-xs font-bold min-w-[1.25rem] text-center
            ${isOnline 
              ? 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200' 
              : 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200'
            }`}
          >
            {queueSize}
          </div>
        )}

        {/* Syncing indicator */}
        {isSyncing && (
          <div className="animate-spin rounded-full h-3 w-3 border border-current border-t-transparent" />
        )}
      </div>

      {/* Details panel */}
      {showDetails && (
        <div className="mt-2 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-w-xs">
          <div className="text-sm space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Connection:</span>
              <span className={`font-medium ${isOnline ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {isOnline ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {queueSize > 0 && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Pending actions:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {queueSize}
                  </span>
                </div>
                
                {isOnline && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      sync();
                    }}
                    disabled={isSyncing}
                    className="w-full mt-2 px-3 py-1.5 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 
                             disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isSyncing ? 'Syncing...' : 'Sync Now'}
                  </button>
                )}
              </>
            )}

            {!isOnline && (
              <div className="text-xs text-gray-500 dark:text-gray-400 pt-1 border-t border-gray-200 dark:border-gray-700">
                Your actions will be saved and synced when connection is restored.
              </div>
            )}

            {isOnline && queueSize === 0 && (
              <div className="text-xs text-gray-500 dark:text-gray-400 pt-1 border-t border-gray-200 dark:border-gray-700">
                All data is up to date.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};