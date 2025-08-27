import React, { useState, useCallback } from 'react';
import {
  CloudArrowDownIcon,
  CloudArrowUpIcon,
  TrashIcon,
  DocumentArrowDownIcon,
  DocumentArrowUpIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '../Shared/Button/Button';
import { useOfflineDescriptions } from '../../hooks/useOfflineDescriptions';
import { useOffline } from '../../hooks/useOffline';
import { formatDistanceToNow } from 'date-fns';

interface OfflineDescriptionManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OfflineDescriptionManager: React.FC<OfflineDescriptionManagerProps> = ({
  isOpen,
  onClose,
}) => {
  const [selectedTab, setSelectedTab] = useState<'cached' | 'pending'>('cached');
  const [importData, setImportData] = useState('');
  const [showImportDialog, setShowImportDialog] = useState(false);
  
  const {
    cachedDescriptions,
    pendingRequests,
    syncPendingRequests,
    clearCache,
    getCacheSize,
    exportCache,
    importCache,
  } = useOfflineDescriptions();
  
  const { isOnline } = useOffline();
  
  const { count, sizeBytes } = getCacheSize();
  
  const handleExport = useCallback(() => {
    const data = exportCache();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `offline-descriptions-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [exportCache]);
  
  const handleImport = useCallback(() => {
    if (importData.trim()) {
      const success = importCache(importData);
      if (success) {
        setImportData('');
        setShowImportDialog(false);
      }
    }
  }, [importData, importCache]);
  
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Panel */}
      <div className="absolute right-0 top-0 h-full w-full max-w-2xl bg-white dark:bg-gray-900 shadow-2xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <CloudArrowDownIcon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Offline Descriptions
              </h2>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="p-2"
              aria-label="Close offline manager"
            >
              ×
            </Button>
          </div>

          {/* Status Bar */}
          <div className="px-6 py-4 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-2 ${
                  isOnline ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    isOnline ? 'bg-green-500' : 'bg-orange-500'
                  }`} />
                  <span className="text-sm font-medium">
                    {isOnline ? 'Online' : 'Offline'}
                  </span>
                </div>
                
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {count} items • {formatBytes(sizeBytes)}
                </div>
              </div>
              
              {isOnline && pendingRequests.length > 0 && (
                <Button size="sm" onClick={syncPendingRequests}>
                  <CloudArrowUpIcon className="w-4 h-4 mr-1" />
                  Sync ({pendingRequests.length})
                </Button>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setSelectedTab('cached')}
              className={`flex-1 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === 'cached'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <CheckCircleIcon className="w-4 h-4" />
                <span>Cached ({cachedDescriptions.length})</span>
              </div>
            </button>
            
            <button
              onClick={() => setSelectedTab('pending')}
              className={`flex-1 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === 'pending'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <ClockIcon className="w-4 h-4" />
                <span>Pending ({pendingRequests.length})</span>
              </div>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {selectedTab === 'cached' ? (
              <div className="space-y-4">
                {cachedDescriptions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <CheckCircleIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No cached descriptions</p>
                    <p className="text-sm">Generated descriptions will be cached here for offline access</p>
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
                            {description.synced ? (
                              <CheckCircleIcon className="w-4 h-4 text-green-500" />
                            ) : (
                              <ExclamationCircleIcon className="w-4 h-4 text-orange-500" />
                            )}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {formatDistanceToNow(new Date(description.timestamp), { addSuffix: true })}
                          </div>
                        </div>
                        
                        <div className="text-right text-sm text-gray-500 dark:text-gray-400">
                          <div>{description.tokenCount} tokens</div>
                          <div>{description.vocabulary.length} vocab</div>
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-3">
                        {description.description}
                      </div>
                      
                      {description.context && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 italic border-l-2 border-gray-200 dark:border-gray-600 pl-2 mb-2">
                          Context: {description.context}
                        </div>
                      )}
                      
                      {description.focusAreas && description.focusAreas.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {description.focusAreas.map((area) => (
                            <span 
                              key={area}
                              className="inline-block px-2 py-1 text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded"
                            >
                              {area}
                            </span>
                          ))}\n                        </div>\n                      )}\n                    </div>\n                  ))\n                )}\n              </div>\n            ) : (\n              <div className=\"space-y-4\">\n                {pendingRequests.length === 0 ? (\n                  <div className=\"text-center py-8 text-gray-500 dark:text-gray-400\">\n                    <ClockIcon className=\"w-12 h-12 mx-auto mb-4 opacity-50\" />\n                    <p>No pending requests</p>\n                    <p className=\"text-sm\">Requests made while offline will appear here</p>\n                  </div>\n                ) : (\n                  pendingRequests.map((request) => (\n                    <div \n                      key={request.id}\n                      className=\"bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4\"\n                    >\n                      <div className=\"flex items-start justify-between mb-3\">\n                        <div className=\"flex-1 min-w-0\">\n                          <div className=\"flex items-center space-x-2 mb-1\">\n                            <span className=\"font-medium text-gray-900 dark:text-gray-100\">\n                              {request.style}\n                            </span>\n                            {request.retryCount > 0 && (\n                              <span className=\"px-2 py-1 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded\">\n                                Retry {request.retryCount}\n                              </span>\n                            )}\n                          </div>\n                          <div className=\"text-sm text-gray-600 dark:text-gray-400\">\n                            {formatDistanceToNow(new Date(request.timestamp), { addSuffix: true })}\n                          </div>\n                        </div>\n                        \n                        <ClockIcon className=\"w-5 h-5 text-orange-500\" />\n                      </div>\n                      \n                      {request.context && (\n                        <div className=\"text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-2\">\n                          Context: {request.context}\n                        </div>\n                      )}\n                      \n                      {request.focusAreas && request.focusAreas.length > 0 && (\n                        <div className=\"flex flex-wrap gap-1\">\n                          {request.focusAreas.map((area) => (\n                            <span \n                              key={area}\n                              className=\"inline-block px-2 py-1 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded\"\n                            >\n                              {area}\n                            </span>\n                          ))}\n                        </div>\n                      )}\n                    </div>\n                  ))\n                )}\n              </div>\n            )}\n          </div>\n\n          {/* Footer Actions */}\n          <div className=\"border-t border-gray-200 dark:border-gray-700 p-6\">\n            <div className=\"flex space-x-3\">\n              <Button\n                variant=\"outline\"\n                onClick={handleExport}\n                disabled={count === 0}\n                className=\"flex items-center space-x-2\"\n              >\n                <DocumentArrowDownIcon className=\"w-4 h-4\" />\n                <span>Export</span>\n              </Button>\n              \n              <Button\n                variant=\"outline\"\n                onClick={() => setShowImportDialog(true)}\n                className=\"flex items-center space-x-2\"\n              >\n                <DocumentArrowUpIcon className=\"w-4 h-4\" />\n                <span>Import</span>\n              </Button>\n              \n              <Button\n                variant=\"outline\"\n                onClick={clearCache}\n                disabled={count === 0}\n                className=\"flex items-center space-x-2 text-red-600 hover:text-red-700\"\n              >\n                <TrashIcon className=\"w-4 h-4\" />\n                <span>Clear All</span>\n              </Button>\n            </div>\n          </div>\n        </div>\n      </div>\n\n      {/* Import Dialog */}\n      {showImportDialog && (\n        <div className=\"fixed inset-0 z-60 flex items-center justify-center p-4\">\n          <div className=\"absolute inset-0 bg-black/50\" onClick={() => setShowImportDialog(false)} />\n          <div className=\"relative bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-lg w-full p-6\">\n            <h3 className=\"text-lg font-medium text-gray-900 dark:text-gray-100 mb-4\">\n              Import Cache Data\n            </h3>\n            \n            <textarea\n              value={importData}\n              onChange={(e) => setImportData(e.target.value)}\n              placeholder=\"Paste exported JSON data here...\"\n              className=\"w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg\n                       bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100\n                       placeholder-gray-500 dark:placeholder-gray-400\n                       focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500\"\n            />\n            \n            <div className=\"flex space-x-3 mt-4\">\n              <Button onClick={handleImport} disabled={!importData.trim()}>\n                Import\n              </Button>\n              <Button variant=\"outline\" onClick={() => setShowImportDialog(false)}>\n                Cancel\n              </Button>\n            </div>\n          </div>\n        </div>\n      )}\n    </div>\n  );\n};"