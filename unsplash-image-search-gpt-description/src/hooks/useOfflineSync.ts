import { useState, useEffect, useCallback } from 'react';
import { OfflineVocabularyChange, ConflictResolution, VocabularyItem } from '../types';
import { vocabularyService } from '../services/vocabularyService';

// IndexedDB utilities for offline storage
class OfflineStorageService {
  private dbName = 'VocabularyApp';
  private version = 1;
  private db: IDBDatabase | null = null;

  async initialize(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = () => {
        const db = request.result;
        
        // Vocabulary items store
        if (!db.objectStoreNames.contains('vocabulary')) {
          const vocabularyStore = db.createObjectStore('vocabulary', { keyPath: 'id' });
          vocabularyStore.createIndex('word', 'word', { unique: false });
          vocabularyStore.createIndex('masteryLevel', 'masteryLevel', { unique: false });
          vocabularyStore.createIndex('updatedAt', 'updatedAt', { unique: false });
        }
        
        // Sync queue store
        if (!db.objectStoreNames.contains('syncQueue')) {
          db.createObjectStore('syncQueue', { keyPath: 'id' });
        }
        
        // Offline sessions store
        if (!db.objectStoreNames.contains('offlineSessions')) {
          db.createObjectStore('offlineSessions', { keyPath: 'id' });
        }
      };
    });
  }

  async getVocabularyItems(): Promise<VocabularyItem[]> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['vocabulary'], 'readonly');
      const store = transaction.objectStore('vocabulary');
      const request = store.getAll();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result || []);
    });
  }

  async saveVocabularyItem(item: VocabularyItem): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['vocabulary'], 'readwrite');
      const store = transaction.objectStore('vocabulary');
      const request = store.put({
        ...item,
        _offline: true,
        _lastModified: Date.now()
      });
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async deleteVocabularyItem(id: string): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['vocabulary'], 'readwrite');
      const store = transaction.objectStore('vocabulary');
      const request = store.delete(id);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async addToSyncQueue(change: OfflineVocabularyChange): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      const request = store.put(change);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async getSyncQueue(): Promise<OfflineVocabularyChange[]> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['syncQueue'], 'readonly');
      const store = transaction.objectStore('syncQueue');
      const request = store.getAll();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result || []);
    });
  }

  async removeSyncItem(id: string): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      const request = store.delete(id);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async clearSyncQueue(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      const request = store.clear();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
}

const offlineStorage = new OfflineStorageService();

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncQueue, setSyncQueue] = useState<OfflineVocabularyChange[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [conflicts, setConflicts] = useState<ConflictResolution[]>([]);

  // Initialize offline storage
  useEffect(() => {
    const initializeStorage = async () => {
      try {
        await offlineStorage.initialize();
        const queue = await offlineStorage.getSyncQueue();
        setSyncQueue(queue);
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize offline storage:', error);
      }
    };

    initializeStorage();
  }, []);

  // Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Automatically sync when coming back online
      if (syncQueue.length > 0) {
        syncOfflineChanges();
      }
    };
    
    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [syncQueue.length]);

  // Add item to sync queue
  const addToSyncQueue = useCallback(async (change: OfflineVocabularyChange) => {
    try {
      await offlineStorage.addToSyncQueue(change);
      setSyncQueue(prev => [...prev, change]);
    } catch (error) {
      console.error('Failed to add to sync queue:', error);
    }
  }, []);

  // Save vocabulary item offline
  const saveOfflineVocabularyItem = useCallback(async (item: VocabularyItem) => {
    try {
      await offlineStorage.saveVocabularyItem(item);
      
      // Add to sync queue
      const change: OfflineVocabularyChange = {
        id: `offline-${Date.now()}`,
        type: item.id ? 'update' : 'create',
        vocabularyId: item.id,
        data: item,
        timestamp: new Date(),
        synced: false
      };
      
      await addToSyncQueue(change);
    } catch (error) {
      console.error('Failed to save vocabulary item offline:', error);
    }
  }, [addToSyncQueue]);

  // Delete vocabulary item offline
  const deleteOfflineVocabularyItem = useCallback(async (id: string) => {
    try {
      await offlineStorage.deleteVocabularyItem(id);
      
      // Add to sync queue
      const change: OfflineVocabularyChange = {
        id: `offline-delete-${Date.now()}`,
        type: 'delete',
        vocabularyId: id,
        timestamp: new Date(),
        synced: false
      };
      
      await addToSyncQueue(change);
    } catch (error) {
      console.error('Failed to delete vocabulary item offline:', error);
    }
  }, [addToSyncQueue]);

  // Get offline vocabulary items
  const getOfflineVocabularyItems = useCallback(async (): Promise<VocabularyItem[]> => {
    try {
      return await offlineStorage.getVocabularyItems();
    } catch (error) {
      console.error('Failed to get offline vocabulary items:', error);
      return [];
    }
  }, []);

  // Sync offline changes with server
  const syncOfflineChanges = useCallback(async () => {
    if (!isOnline || isSyncing || syncQueue.length === 0) return;
    
    setIsSyncing(true);
    
    try {
      const unsynced = syncQueue.filter(item => !item.synced);
      
      if (unsynced.length === 0) {
        setIsSyncing(false);
        return;
      }
      
      // Sync changes with server
      const serverConflicts = await vocabularyService.syncOfflineChanges(unsynced);
      
      if (serverConflicts.length > 0) {
        setConflicts(serverConflicts);
      }
      
      // Remove synced items from queue
      for (const change of unsynced) {
        await offlineStorage.removeSyncItem(change.id);
      }
      
      // Update local sync queue
      const updatedQueue = await offlineStorage.getSyncQueue();
      setSyncQueue(updatedQueue);
      
      console.log(`Successfully synced ${unsynced.length} changes`);
      
    } catch (error) {
      console.error('Failed to sync offline changes:', error);
    } finally {
      setIsSyncing(false);
    }
  }, [isOnline, isSyncing, syncQueue]);

  // Resolve conflict
  const resolveConflict = useCallback(async (
    conflict: ConflictResolution, 
    resolution: 'local' | 'remote' | 'merge'
  ) => {
    try {
      let resolvedItem: VocabularyItem;
      
      switch (resolution) {
        case 'local':
          resolvedItem = conflict.localItem;
          break;
        case 'remote':
          resolvedItem = conflict.remoteItem;
          break;
        case 'merge':
          resolvedItem = conflict.mergedItem || conflict.remoteItem;
          break;
        default:
          resolvedItem = conflict.remoteItem;
      }
      
      // Update the item on the server
      await vocabularyService.updateVocabularyItem(resolvedItem.id, resolvedItem);
      
      // Update offline storage
      await offlineStorage.saveVocabularyItem(resolvedItem);
      
      // Remove from conflicts
      setConflicts(prev => prev.filter(c => 
        c.localItem.id !== conflict.localItem.id
      ));
      
    } catch (error) {
      console.error('Failed to resolve conflict:', error);
    }
  }, []);

  // Clear all offline data
  const clearOfflineData = useCallback(async () => {
    try {
      await offlineStorage.clearSyncQueue();
      setSyncQueue([]);
      setConflicts([]);
    } catch (error) {
      console.error('Failed to clear offline data:', error);
    }
  }, []);

  // Manual sync trigger
  const triggerSync = useCallback(() => {
    if (isOnline && !isSyncing) {
      syncOfflineChanges();
    }
  }, [isOnline, isSyncing, syncOfflineChanges]);

  // Background sync when online
  useEffect(() => {
    if (isOnline && isInitialized && syncQueue.length > 0 && !isSyncing) {
      const syncTimeout = setTimeout(() => {
        syncOfflineChanges();
      }, 2000); // Delay sync by 2 seconds to avoid rapid syncing
      
      return () => clearTimeout(syncTimeout);
    }
  }, [isOnline, isInitialized, syncQueue.length, isSyncing, syncOfflineChanges]);

  return {
    isOnline,
    isInitialized,
    isSyncing,
    syncQueue,
    conflicts,
    
    // Actions
    addToSyncQueue,
    saveOfflineVocabularyItem,
    deleteOfflineVocabularyItem,
    getOfflineVocabularyItems,
    syncOfflineChanges,
    resolveConflict,
    clearOfflineData,
    triggerSync,
    
    // Status
    hasPendingChanges: syncQueue.length > 0,
    hasConflicts: conflicts.length > 0
  };
}