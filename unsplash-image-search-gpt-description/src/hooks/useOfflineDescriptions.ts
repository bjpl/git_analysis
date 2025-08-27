import { useState, useCallback, useEffect } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { useOffline } from './useOffline';
import { VocabularyWord, DescriptionStyle } from '../types';
import toast from 'react-hot-toast';

interface OfflineDescription {
  id: string;
  imageId: string;
  imageUrl: string;
  style: DescriptionStyle;
  description: string;
  vocabulary: VocabularyWord[];
  context?: string;
  focusAreas?: string[];
  tokenCount: number;
  processingTime: number;
  timestamp: number;
  synced: boolean;
  version: number;
}

interface OfflineDescriptionRequest {
  id: string;
  imageId: string;
  imageUrl: string;
  style: DescriptionStyle;
  context?: string;
  focusAreas?: string[];
  vocabularyLevel: 1 | 2 | 3 | 4 | 5;
  timestamp: number;
  retryCount: number;
}

interface UseOfflineDescriptionsReturn {
  cachedDescriptions: OfflineDescription[];
  pendingRequests: OfflineDescriptionRequest[];
  cacheDescription: (description: OfflineDescription) => void;
  getCachedDescription: (imageId: string, style: DescriptionStyle, context?: string, focusAreas?: string[]) => OfflineDescription | null;
  queueOfflineRequest: (request: Omit<OfflineDescriptionRequest, 'id' | 'timestamp' | 'retryCount'>) => void;
  syncPendingRequests: () => Promise<void>;
  clearCache: () => void;
  getCacheSize: () => { count: number; sizeBytes: number };
  exportCache: () => string;
  importCache: (data: string) => boolean;
}

const CACHE_KEY = 'offline-descriptions';
const REQUESTS_KEY = 'pending-description-requests';
const MAX_CACHE_SIZE = 100; // Maximum number of cached descriptions
const MAX_RETRY_COUNT = 3;

// Utility functions
const generateCacheKey = (imageId: string, style: DescriptionStyle, context?: string, focusAreas?: string[]): string => {
  const contextHash = context ? btoa(unescape(encodeURIComponent(context))).slice(0, 8) : '';
  const focusHash = focusAreas?.length ? btoa(focusAreas.join(',')).slice(0, 8) : '';
  return `${imageId}_${style}_${contextHash}_${focusHash}`;
};

const calculateObjectSize = (obj: any): number => {
  return new Blob([JSON.stringify(obj)]).size;
};

export const useOfflineDescriptions = (): UseOfflineDescriptionsReturn => {
  const [cachedDescriptions, setCachedDescriptions] = useLocalStorage<OfflineDescription[]>(CACHE_KEY, []);
  const [pendingRequests, setPendingRequests] = useLocalStorage<OfflineDescriptionRequest[]>(REQUESTS_KEY, []);
  const { isOnline } = useOffline();
  const [syncInProgress, setSyncInProgress] = useState(false);

  // Auto-sync when coming back online
  useEffect(() => {
    if (isOnline && pendingRequests.length > 0 && !syncInProgress) {
      syncPendingRequests();
    }
  }, [isOnline, pendingRequests.length, syncInProgress]);

  // Cleanup old cache entries periodically
  useEffect(() => {
    const cleanup = () => {
      setCachedDescriptions(prev => {
        // Remove entries older than 30 days
        const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
        const filtered = prev.filter(item => item.timestamp > thirtyDaysAgo);
        
        // If still too many, keep only the most recent ones
        if (filtered.length > MAX_CACHE_SIZE) {
          return filtered
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, MAX_CACHE_SIZE);
        }
        
        return filtered;
      });
    };

    // Run cleanup on mount and then periodically
    cleanup();
    const interval = setInterval(cleanup, 60 * 60 * 1000); // Every hour
    
    return () => clearInterval(interval);
  }, [setCachedDescriptions]);

  const cacheDescription = useCallback((description: OfflineDescription) => {
    setCachedDescriptions(prev => {
      // Remove any existing description with the same key
      const cacheKey = generateCacheKey(
        description.imageId, 
        description.style, 
        description.context, 
        description.focusAreas
      );
      
      const filtered = prev.filter(item => {
        const itemKey = generateCacheKey(item.imageId, item.style, item.context, item.focusAreas);
        return itemKey !== cacheKey;
      });
      
      // Add new description
      const updated = [description, ...filtered];
      
      // Limit cache size
      if (updated.length > MAX_CACHE_SIZE) {
        return updated
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, MAX_CACHE_SIZE);
      }
      
      return updated;
    });
  }, [setCachedDescriptions]);

  const getCachedDescription = useCallback((
    imageId: string, 
    style: DescriptionStyle, 
    context?: string, 
    focusAreas?: string[]
  ): OfflineDescription | null => {
    const cacheKey = generateCacheKey(imageId, style, context, focusAreas);
    
    const cached = cachedDescriptions.find(item => {
      const itemKey = generateCacheKey(item.imageId, item.style, item.context, item.focusAreas);
      return itemKey === cacheKey;
    });
    
    if (cached) {
      // Check if cache is still valid (24 hours for offline, 1 hour for online)
      const maxAge = isOnline ? 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
      const isExpired = Date.now() - cached.timestamp > maxAge;
      
      if (isExpired && isOnline) {
        // Remove expired cache entry when online
        setCachedDescriptions(prev => prev.filter(item => item.id !== cached.id));
        return null;
      }
      
      return cached;
    }
    
    return null;
  }, [cachedDescriptions, isOnline, setCachedDescriptions]);

  const queueOfflineRequest = useCallback((request: Omit<OfflineDescriptionRequest, 'id' | 'timestamp' | 'retryCount'>) => {
    const queuedRequest: OfflineDescriptionRequest = {
      ...request,
      id: `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      retryCount: 0,
    };
    
    setPendingRequests(prev => {
      // Avoid duplicates
      const exists = prev.some(item => 
        item.imageId === queuedRequest.imageId && 
        item.style === queuedRequest.style &&
        JSON.stringify(item.context) === JSON.stringify(queuedRequest.context) &&
        JSON.stringify(item.focusAreas) === JSON.stringify(queuedRequest.focusAreas)
      );
      
      if (exists) {
        return prev;
      }
      
      return [...prev, queuedRequest];
    });
    
    toast.info('Request queued for when you\'re back online');
  }, [setPendingRequests]);

  const syncPendingRequests = useCallback(async () => {
    if (!isOnline || pendingRequests.length === 0 || syncInProgress) {
      return;
    }

    setSyncInProgress(true);
    
    try {
      const requestsToProcess = [...pendingRequests];
      const successfulRequests: string[] = [];
      const failedRequests: OfflineDescriptionRequest[] = [];
      
      for (const request of requestsToProcess) {
        try {
          // Simulate API call to generate description
          const response = await fetch('/api/generate-description', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              imageId: request.imageId,
              imageUrl: request.imageUrl,
              style: request.style,
              context: request.context,
              focusAreas: request.focusAreas,
              vocabularyLevel: request.vocabularyLevel,
            }),
            signal: AbortSignal.timeout(30000), // 30 second timeout
          });
          
          if (response.ok) {
            const data = await response.json();
            
            // Cache the successful response
            const description: OfflineDescription = {
              id: `synced_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              imageId: request.imageId,
              imageUrl: request.imageUrl,
              style: request.style,
              description: data.description || 'Description generated successfully',
              vocabulary: data.vocabulary || [],
              context: request.context,
              focusAreas: request.focusAreas,
              tokenCount: data.tokenCount || 0,
              processingTime: data.processingTime || 0,
              timestamp: Date.now(),
              synced: true,
              version: 1,
            };
            
            cacheDescription(description);
            successfulRequests.push(request.id);
          } else {
            // Handle failed request
            const updatedRequest: OfflineDescriptionRequest = {
              ...request,
              retryCount: request.retryCount + 1,
            };
            
            if (updatedRequest.retryCount < MAX_RETRY_COUNT) {
              failedRequests.push(updatedRequest);
            }
          }
        } catch (error) {
          console.error(`Failed to sync request ${request.id}:`, error);
          
          const updatedRequest: OfflineDescriptionRequest = {
            ...request,
            retryCount: request.retryCount + 1,
          };
          
          if (updatedRequest.retryCount < MAX_RETRY_COUNT) {
            failedRequests.push(updatedRequest);
          }
        }
      }
      
      // Update pending requests
      setPendingRequests(failedRequests);
      
      if (successfulRequests.length > 0) {
        toast.success(`Synced ${successfulRequests.length} offline requests`);
      }
      
      if (failedRequests.length > 0) {
        toast.warning(`${failedRequests.length} requests still pending`);
      }
      
    } catch (error) {
      console.error('Sync failed:', error);
      toast.error('Failed to sync offline requests');
    } finally {
      setSyncInProgress(false);
    }
  }, [isOnline, pendingRequests, syncInProgress, setPendingRequests, cacheDescription]);

  const clearCache = useCallback(() => {
    setCachedDescriptions([]);
    setPendingRequests([]);
    toast.success('Cache cleared');
  }, [setCachedDescriptions, setPendingRequests]);

  const getCacheSize = useCallback((): { count: number; sizeBytes: number } => {
    const count = cachedDescriptions.length + pendingRequests.length;
    const sizeBytes = calculateObjectSize(cachedDescriptions) + calculateObjectSize(pendingRequests);
    
    return { count, sizeBytes };
  }, [cachedDescriptions, pendingRequests]);

  const exportCache = useCallback((): string => {
    const exportData = {
      cachedDescriptions,
      pendingRequests,
      exportedAt: new Date().toISOString(),
      version: 1,
    };
    
    return JSON.stringify(exportData, null, 2);
  }, [cachedDescriptions, pendingRequests]);

  const importCache = useCallback((data: string): boolean => {
    try {
      const parsed = JSON.parse(data);
      
      if (parsed.version !== 1) {
        toast.error('Unsupported cache format version');
        return false;
      }
      
      if (Array.isArray(parsed.cachedDescriptions)) {
        setCachedDescriptions(parsed.cachedDescriptions);
      }
      
      if (Array.isArray(parsed.pendingRequests)) {
        setPendingRequests(parsed.pendingRequests);
      }
      
      toast.success('Cache imported successfully');
      return true;
      
    } catch (error) {
      console.error('Failed to import cache:', error);
      toast.error('Failed to import cache data');
      return false;
    }
  }, [setCachedDescriptions, setPendingRequests]);

  return {
    cachedDescriptions,
    pendingRequests,
    cacheDescription,
    getCachedDescription,
    queueOfflineRequest,
    syncPendingRequests,
    clearCache,
    getCacheSize,
    exportCache,
    importCache,
  };
};