import React, { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import {
  ClockIcon,
  DocumentArrowDownIcon,
  DocumentArrowUpIcon,
  TrashIcon,
  WifiIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { Button } from '../Shared/Button/Button';
import { Badge } from '../Shared/Badge/Badge';
import { OfflineDescriptionCache, CachedDescription, PendingRequest } from '../../types/offline';

interface OfflineDescriptionManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function OfflineDescriptionManager({ 
  isOpen, 
  onClose 
}: OfflineDescriptionManagerProps) {
  const [activeTab, setActiveTab] = useState<'cached' | 'pending'>('cached');
  const [cachedDescriptions, setCachedDescriptions] = useState<CachedDescription[]>([]);
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([]);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [importData, setImportData] = useState('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    if (isOpen) {
      loadCachedData();
      loadPendingRequests();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadCachedData = async () => {
    try {
      const cache = await OfflineDescriptionCache.getInstance();
      const descriptions = await cache.getAllDescriptions();
      setCachedDescriptions(descriptions);
    } catch (error) {
      console.error('Failed to load cached descriptions:', error);
    }
  };

  const loadPendingRequests = async () => {
    try {
      const cache = await OfflineDescriptionCache.getInstance();
      const requests = await cache.getPendingRequests();
      setPendingRequests(requests);
    } catch (error) {
      console.error('Failed to load pending requests:', error);
    }
  };

  const handleExport = async () => {
    try {
      const cache = await OfflineDescriptionCache.getInstance();
      const exportData = await cache.exportData();
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vocablens-offline-cache-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleImport = async () => {
    try {
      const data = JSON.parse(importData);
      const cache = await OfflineDescriptionCache.getInstance();
      await cache.importData(data);
      
      setImportData('');
      setShowImportDialog(false);
      
      // Reload data
      await loadCachedData();
      await loadPendingRequests();
    } catch (error) {
      console.error('Import failed:', error);
      alert('Import failed. Please check the data format.');
    }
  };

  const clearCache = async () => {
    if (confirm('Are you sure you want to clear all offline data?')) {
      try {
        const cache = await OfflineDescriptionCache.getInstance();
        await cache.clear();
        
        setCachedDescriptions([]);
        setPendingRequests([]);
      } catch (error) {
        console.error('Failed to clear cache:', error);
      }
    }
  };

  const retryPendingRequest = async (requestId: string) => {
    try {
      const cache = await OfflineDescriptionCache.getInstance();
      await cache.retryRequest(requestId);
      await loadPendingRequests();
    } catch (error) {
      console.error('Failed to retry request:', error);
    }
  };

  const deleteCachedDescription = async (id: string) => {
    try {
      const cache = await OfflineDescriptionCache.getInstance();
      await cache.deleteDescription(id);
      await loadCachedData();
    } catch (error) {
      console.error('Failed to delete description:', error);
    }
  };

  if (!isOpen) return null;

  const count = cachedDescriptions.length;
  const pendingCount = pendingRequests.length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-black/50" 
        onClick={onClose}
      />
      
      <div className="relative bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Offline Manager
            </h2>
            
            <div className="flex items-center space-x-2">
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                isOnline 
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                  : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
              }`}>
                <WifiIcon className="w-3 h-3" />
                <span>{isOnline ? 'Online' : 'Offline'}</span>
              </div>
            </div>
          </div>
          
          <Button
            variant="ghost"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </Button>
        </div>

        {/* Stats */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-800/50">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {count}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Cached Descriptions
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-500">
                {pendingCount}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Pending Requests
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('cached')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'cached'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            Cached Descriptions ({count})
          </button>
          
          <button
            onClick={() => setActiveTab('pending')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'pending'
                ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            Pending Requests ({pendingCount})
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto max-h-96">
          <div className="p-6">
            {activeTab === 'cached' ? (
              <div className="space-y-4">
                {cachedDescriptions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <InformationCircleIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No cached descriptions</p>
                    <p className="text-sm">Descriptions will be cached when you browse offline</p>
                  </div>
                ) : (
                  cachedDescriptions.map((description) => (
                    <div 
                      key={description.id}
                      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {description.style}
                            </span>
                            <Badge variant="success" size="sm">
                              Cached
                            </Badge>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {formatDistanceToNow(new Date(description.cachedAt), { addSuffix: true })}
                          </div>
                        </div>
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteCachedDescription(description.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </Button>
                      </div>
                      
                      <div className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3 mb-3">
                        {description.content}
                      </div>
                      
                      {description.focusAreas && description.focusAreas.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {description.focusAreas.map((area) => (
                            <span 
                              key={area}
                              className="inline-block px-2 py-1 text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded"
                            >
                              {area}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {pendingRequests.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <ClockIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No pending requests</p>
                    <p className="text-sm">Requests made while offline will appear here</p>
                  </div>
                ) : (
                  pendingRequests.map((request) => (
                    <div 
                      key={request.id}
                      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {request.style}
                            </span>
                            {request.retryCount > 0 && (
                              <Badge variant="warning" size="sm">
                                Retry {request.retryCount}
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {formatDistanceToNow(new Date(request.timestamp), { addSuffix: true })}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {isOnline && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => retryPendingRequest(request.id)}
                              className="text-indigo-600 hover:text-indigo-700"
                            >
                              Retry
                            </Button>
                          )}
                          <ClockIcon className="w-5 h-5 text-orange-500" />
                        </div>
                      </div>
                      
                      {request.context && (
                        <div className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-2">
                          Context: {request.context}
                        </div>
                      )}
                      
                      {request.focusAreas && request.focusAreas.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {request.focusAreas.map((area) => (
                            <span 
                              key={area}
                              className="inline-block px-2 py-1 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded"
                            >
                              {area}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6">
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={count === 0}
              className="flex items-center space-x-2"
            >
              <DocumentArrowDownIcon className="w-4 h-4" />
              <span>Export</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={() => setShowImportDialog(true)}
              className="flex items-center space-x-2"
            >
              <DocumentArrowUpIcon className="w-4 h-4" />
              <span>Import</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={clearCache}
              disabled={count === 0}
              className="flex items-center space-x-2 text-red-600 hover:text-red-700"
            >
              <TrashIcon className="w-4 h-4" />
              <span>Clear All</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Import Dialog */}
      {showImportDialog && (
        <div className="fixed inset-0 z-60 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowImportDialog(false)} />
          <div className="relative bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-lg w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Import Cache Data
            </h3>
            
            <textarea
              value={importData}
              onChange={(e) => setImportData(e.target.value)}
              placeholder="Paste exported JSON data here..."
              className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                       placeholder-gray-500 dark:placeholder-gray-400
                       focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            
            <div className="flex space-x-3 mt-4">
              <Button onClick={handleImport} disabled={!importData.trim()}>
                Import
              </Button>
              <Button variant="outline" onClick={() => setShowImportDialog(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}