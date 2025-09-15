/**
 * Note Sync Hook
 * Handles auto-save, sync status, and conflict resolution
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { notesService } from '../services/NotesService.js';

const SYNC_STATES = {
  IDLE: 'idle',
  SYNCING: 'syncing',
  SUCCESS: 'success',
  ERROR: 'error',
  CONFLICT: 'conflict'
};

const AUTO_SAVE_INTERVAL = 5000; // 5 seconds
const SYNC_RETRY_DELAY = 2000; // 2 seconds
const MAX_RETRY_ATTEMPTS = 3;

const INITIAL_SYNC_STATE = {
  status: SYNC_STATES.IDLE,
  lastSync: null,
  lastError: null,
  pendingChanges: 0,
  conflicts: [],
  retryCount: 0
};

export function useNoteSync(options = {}) {
  const {
    enableAutoSave = true,
    autoSaveInterval = AUTO_SAVE_INTERVAL,
    enableRetry = true,
    maxRetryAttempts = MAX_RETRY_ATTEMPTS,
    onSyncSuccess = null,
    onSyncError = null,
    onConflict = null
  } = options;

  const [syncState, setSyncState] = useState(INITIAL_SYNC_STATE);
  const [queuedNotes, setQueuedNotes] = useState(new Map());
  
  const syncTimerRef = useRef(null);
  const retryTimerRef = useRef(null);
  const isProcessingRef = useRef(false);
  const lastSyncVersionsRef = useRef(new Map());

  /**
   * Queue a note for syncing
   */
  const queueNote = useCallback((note, operation = 'update') => {
    setQueuedNotes(prev => {
      const newQueue = new Map(prev);
      newQueue.set(note.id, {
        note: { ...note },
        operation,
        timestamp: Date.now(),
        attempts: 0
      });
      return newQueue;
    });

    setSyncState(prev => ({
      ...prev,
      pendingChanges: prev.pendingChanges + 1,
      status: SYNC_STATES.IDLE
    }));

    // Trigger auto-save if enabled
    if (enableAutoSave && !syncTimerRef.current) {
      syncTimerRef.current = setTimeout(() => {
        processSyncQueue();
      }, autoSaveInterval);
    }
  }, [enableAutoSave, autoSaveInterval]);

  /**
   * Process the sync queue
   */
  const processSyncQueue = useCallback(async () => {
    if (isProcessingRef.current || queuedNotes.size === 0) {
      return;
    }

    isProcessingRef.current = true;
    setSyncState(prev => ({ ...prev, status: SYNC_STATES.SYNCING }));

    try {
      const syncPromises = [];
      const currentQueue = Array.from(queuedNotes.entries());

      for (const [noteId, queueItem] of currentQueue) {
        syncPromises.push(syncSingleNote(noteId, queueItem));
      }

      const results = await Promise.allSettled(syncPromises);
      
      let successCount = 0;
      let errorCount = 0;
      const newConflicts = [];

      results.forEach((result, index) => {
        const [noteId] = currentQueue[index];
        
        if (result.status === 'fulfilled') {
          if (result.value.success) {
            successCount++;
            // Remove from queue
            setQueuedNotes(prev => {
              const newQueue = new Map(prev);
              newQueue.delete(noteId);
              return newQueue;
            });
          } else if (result.value.conflict) {
            newConflicts.push(result.value.conflict);
          } else {
            errorCount++;
          }
        } else {
          errorCount++;
        }
      });

      // Update sync state
      setSyncState(prev => ({
        ...prev,
        status: errorCount > 0 ? SYNC_STATES.ERROR : 
               newConflicts.length > 0 ? SYNC_STATES.CONFLICT : 
               SYNC_STATES.SUCCESS,
        lastSync: new Date(),
        pendingChanges: Math.max(0, prev.pendingChanges - successCount),
        conflicts: [...prev.conflicts, ...newConflicts],
        retryCount: errorCount > 0 ? prev.retryCount + 1 : 0,
        lastError: errorCount > 0 ? `Failed to sync ${errorCount} notes` : null
      }));

      // Trigger callbacks
      if (successCount > 0) {
        onSyncSuccess?.({ syncedCount: successCount });
      }
      
      if (errorCount > 0) {
        onSyncError?.({ errorCount, retryCount: syncState.retryCount + 1 });
      }

      if (newConflicts.length > 0) {
        onConflict?.(newConflicts);
      }

      // Schedule retry if there are failures and retries are enabled
      if (errorCount > 0 && enableRetry && syncState.retryCount < maxRetryAttempts) {
        scheduleRetry();
      }

    } catch (error) {
      console.error('Sync queue processing failed:', error);
      setSyncState(prev => ({
        ...prev,
        status: SYNC_STATES.ERROR,
        lastError: error.message,
        retryCount: prev.retryCount + 1
      }));

      onSyncError?.({ error, retryCount: syncState.retryCount + 1 });

      if (enableRetry && syncState.retryCount < maxRetryAttempts) {
        scheduleRetry();
      }
    } finally {
      isProcessingRef.current = false;
      
      // Clear timer
      if (syncTimerRef.current) {
        clearTimeout(syncTimerRef.current);
        syncTimerRef.current = null;
      }
    }
  }, [queuedNotes, enableRetry, maxRetryAttempts, syncState.retryCount, onSyncSuccess, onSyncError, onConflict]);

  /**
   * Sync a single note
   */
  const syncSingleNote = useCallback(async (noteId, queueItem) => {
    try {
      const { note, operation, attempts } = queueItem;
      
      // Check for conflicts before syncing
      if (operation === 'update' && note.id) {
        const currentNote = await notesService.read(note.id);
        const lastKnownVersion = lastSyncVersionsRef.current.get(note.id);
        
        if (lastKnownVersion && currentNote.updatedAt !== lastKnownVersion) {
          // Conflict detected
          return {
            success: false,
            conflict: {
              noteId: note.id,
              localNote: note,
              serverNote: currentNote,
              conflictType: 'concurrent_modification'
            }
          };
        }
      }

      let result;
      switch (operation) {
        case 'create':
          result = await notesService.create(note);
          break;
        case 'update':
          result = await notesService.update(note.id, note);
          break;
        case 'delete':
          result = await notesService.delete(note.id);
          break;
        default:
          throw new Error(`Unknown sync operation: ${operation}`);
      }

      // Update version tracking
      if (result && result.id) {
        lastSyncVersionsRef.current.set(result.id, result.updatedAt);
      }

      return { success: true, result };

    } catch (error) {
      console.error(`Failed to sync note ${noteId}:`, error);
      
      // Update queue item with attempt count
      setQueuedNotes(prev => {
        const newQueue = new Map(prev);
        const item = newQueue.get(noteId);
        if (item) {
          newQueue.set(noteId, { ...item, attempts: item.attempts + 1 });
        }
        return newQueue;
      });

      return { success: false, error: error.message };
    }
  }, []);

  /**
   * Schedule a retry attempt
   */
  const scheduleRetry = useCallback(() => {
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current);
    }

    retryTimerRef.current = setTimeout(() => {
      processSyncQueue();
    }, SYNC_RETRY_DELAY * Math.pow(2, syncState.retryCount)); // Exponential backoff
  }, [processSyncQueue, syncState.retryCount]);

  /**
   * Force sync now
   */
  const forcSync = useCallback(async () => {
    if (syncTimerRef.current) {
      clearTimeout(syncTimerRef.current);
      syncTimerRef.current = null;
    }

    await processSyncQueue();
  }, [processSyncQueue]);

  /**
   * Resolve a conflict
   */
  const resolveConflict = useCallback((conflictId, resolution) => {
    setSyncState(prev => {
      const conflict = prev.conflicts.find(c => c.noteId === conflictId);
      if (!conflict) return prev;

      let noteToSync;
      switch (resolution.type) {
        case 'use_local':
          noteToSync = conflict.localNote;
          break;
        case 'use_server':
          noteToSync = conflict.serverNote;
          // Update version tracking
          lastSyncVersionsRef.current.set(conflict.noteId, conflict.serverNote.updatedAt);
          return {
            ...prev,
            conflicts: prev.conflicts.filter(c => c.noteId !== conflictId)
          };
        case 'merge':
          noteToSync = resolution.mergedNote;
          break;
        default:
          throw new Error(`Unknown conflict resolution type: ${resolution.type}`);
      }

      // Queue the resolved note for sync
      queueNote(noteToSync, 'update');

      return {
        ...prev,
        conflicts: prev.conflicts.filter(c => c.noteId !== conflictId)
      };
    });
  }, [queueNote]);

  /**
   * Clear sync errors
   */
  const clearSyncError = useCallback(() => {
    setSyncState(prev => ({
      ...prev,
      status: prev.conflicts.length > 0 ? SYNC_STATES.CONFLICT : SYNC_STATES.IDLE,
      lastError: null,
      retryCount: 0
    }));
  }, []);

  /**
   * Get sync statistics
   */
  const getSyncStats = useCallback(() => {
    const queuedItems = Array.from(queuedNotes.values());
    
    return {
      pendingChanges: syncState.pendingChanges,
      queueSize: queuedNotes.size,
      conflictsCount: syncState.conflicts.length,
      retryCount: syncState.retryCount,
      lastSync: syncState.lastSync,
      status: syncState.status,
      oldestQueuedItem: queuedItems.reduce((oldest, item) => 
        !oldest || item.timestamp < oldest.timestamp ? item : oldest, null
      )?.timestamp || null
    };
  }, [syncState, queuedNotes]);

  /**
   * Pause/resume auto-sync
   */
  const [isPaused, setIsPaused] = useState(false);
  
  const pauseSync = useCallback(() => {
    setIsPaused(true);
    if (syncTimerRef.current) {
      clearTimeout(syncTimerRef.current);
      syncTimerRef.current = null;
    }
  }, []);

  const resumeSync = useCallback(() => {
    setIsPaused(false);
    if (enableAutoSave && queuedNotes.size > 0) {
      syncTimerRef.current = setTimeout(processSyncQueue, 1000);
    }
  }, [enableAutoSave, queuedNotes.size, processSyncQueue]);

  // Auto-sync effect
  useEffect(() => {
    if (!enableAutoSave || isPaused || queuedNotes.size === 0) {
      return;
    }

    if (syncTimerRef.current) {
      clearTimeout(syncTimerRef.current);
    }

    syncTimerRef.current = setTimeout(() => {
      processSyncQueue();
    }, autoSaveInterval);

    return () => {
      if (syncTimerRef.current) {
        clearTimeout(syncTimerRef.current);
      }
    };
  }, [queuedNotes.size, enableAutoSave, autoSaveInterval, isPaused, processSyncQueue]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (syncTimerRef.current) {
        clearTimeout(syncTimerRef.current);
      }
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
      }
    };
  }, []);

  return {
    // State
    syncStatus: syncState.status,
    pendingChanges: syncState.pendingChanges,
    conflicts: syncState.conflicts,
    lastSync: syncState.lastSync,
    lastError: syncState.lastError,
    retryCount: syncState.retryCount,
    isPaused,

    // Actions
    queueNote,
    forcSync,
    resolveConflict,
    clearSyncError,
    pauseSync,
    resumeSync,
    getSyncStats,

    // Status helpers
    isSyncing: syncState.status === SYNC_STATES.SYNCING,
    hasConflicts: syncState.conflicts.length > 0,
    hasErrors: syncState.status === SYNC_STATES.ERROR,
    isIdle: syncState.status === SYNC_STATES.IDLE,
    canRetry: enableRetry && syncState.retryCount < maxRetryAttempts,

    // Queue info
    queueSize: queuedNotes.size,
    hasQueuedChanges: queuedNotes.size > 0
  };
}