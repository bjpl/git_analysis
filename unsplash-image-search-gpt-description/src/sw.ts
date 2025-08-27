/**
 * Service Worker for VocabLens PWA
 * 
 * Provides comprehensive offline functionality with:
 * - Advanced caching strategies
 * - Background sync
 * - Push notifications
 * - Resource prioritization
 * - Performance optimization
 */

import {
  cleanupOutdatedCaches,
  createHandlerBoundToURL,
  precacheAndRoute,
  NavigationRoute,
  registerRoute,
} from 'workbox-precaching';
import {
  CacheFirst,
  NetworkFirst,
  NetworkOnly,
  StaleWhileRevalidate,
} from 'workbox-strategies';
import {
  CacheableResponsePlugin,
  ExpirationPlugin,
  BackgroundSyncPlugin,
  BroadcastUpdatePlugin,
} from 'workbox-plugins';
import { BackgroundSync } from 'workbox-background-sync';

declare const self: ServiceWorkerGlobalScope;

// Precache and route
precacheAndRoute(self.__WB_MANIFEST);

// Clean up outdated caches
cleanupOutdatedCaches();

// Background sync instances
const vocabularySync = new BackgroundSync('vocabulary-queue', {
  maxRetentionTime: 24 * 60, // 24 hours
});

const analyticsSync = new BackgroundSync('analytics-queue', {
  maxRetentionTime: 12 * 60, // 12 hours
});

const sessionSync = new BackgroundSync('session-queue', {
  maxRetentionTime: 24 * 60, // 24 hours
});

// Cache strategies

// 1. Unsplash Images - Cache First with long expiration
registerRoute(
  /^https:\/\/images\.unsplash\.com\/.*/i,
  new CacheFirst({
    cacheName: 'unsplash-images-v1',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 300,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
        purgeOnQuotaError: true,
      }),
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new BroadcastUpdatePlugin({
        headersToCheck: ['last-modified', 'etag'],
      }),
    ],
  })
);

// 2. Supabase API - Network First with short cache
registerRoute(
  /^https:\/\/.*\.supabase\.co\/rest\/.*/i,
  new NetworkFirst({
    cacheName: 'supabase-api-v1',
    networkTimeoutSeconds: 5,
    plugins: [
      new ExpirationPlugin({
        maxEntries: 150,
        maxAgeSeconds: 10 * 60, // 10 minutes
      }),
      new CacheableResponsePlugin({
        statuses: [200],
      }),
      new BackgroundSyncPlugin({
        name: 'api-sync-queue',
        options: {
          maxRetentionTime: 24 * 60, // 24 hours
        },
      }),
    ],
  })
);

// 3. Supabase Auth - Network Only (never cache auth)
registerRoute(
  /^https:\/\/.*\.supabase\.co\/auth\/.*/i,
  new NetworkOnly()
);

// 4. Google Fonts - Stale While Revalidate
registerRoute(
  /^https:\/\/fonts\.googleapis\.com\/.*/i,
  new StaleWhileRevalidate({
    cacheName: 'google-fonts-stylesheets-v1',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 10,
        maxAgeSeconds: 365 * 24 * 60 * 60, // 1 year
      }),
    ],
  })
);

registerRoute(
  /^https:\/\/fonts\.gstatic\.com\/.*/i,
  new CacheFirst({
    cacheName: 'google-fonts-webfonts-v1',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 365 * 24 * 60 * 60, // 1 year
      }),
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
    ],
  })
);

// 5. Static Images - Cache First
registerRoute(
  /\.(?:png|jpg|jpeg|svg|gif|webp|ico)$/,
  new CacheFirst({
    cacheName: 'static-images-v1',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
    ],
  })
);

// 6. CSS and JS - Stale While Revalidate
registerRoute(
  /\.(?:js|css)$/,
  new StaleWhileRevalidate({
    cacheName: 'static-resources-v1',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 7 * 24 * 60 * 60, // 1 week
      }),
    ],
  })
);

// 7. App Shell - Network First with fallback
const navigationHandler = createHandlerBoundToURL('/index.html');
const navigationRoute = new NavigationRoute(navigationHandler, {
  denylist: [/^\/_/, /\/[^/?]+\.[^/]+$/],
});
registerRoute(navigationRoute);

// Background Sync Event Handlers

// Vocabulary sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'vocabulary-sync') {
    event.waitUntil(handleVocabularySync());
  } else if (event.tag === 'analytics-sync') {
    event.waitUntil(handleAnalyticsSync());
  } else if (event.tag === 'session-sync') {
    event.waitUntil(handleSessionSync());
  }
});

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('Push notification received:', event);
  
  if (!event.data) return;

  const options = {
    body: event.data.text(),
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    tag: 'vocab-reminder',
    renotify: true,
    requireInteraction: true,
    actions: [
      {
        action: 'open',
        title: 'Open VocabLens',
        icon: '/icons/action-open.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/icons/action-dismiss.png'
      }
    ],
    data: {
      timestamp: Date.now(),
      url: '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification('VocabLens Reminder', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Check if there's already an open window
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
    );
  }
});

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type) {
    switch (event.data.type) {
      case 'SKIP_WAITING':
        self.skipWaiting();
        break;
        
      case 'CACHE_NEW_ROUTE':
        handleCacheNewRoute(event.data.url);
        break;
        
      case 'QUEUE_SYNC':
        handleQueueSync(event.data.data, event.data.syncType);
        break;
        
      case 'CLEAR_CACHE':
        handleClearCache(event.data.cacheName);
        break;
        
      case 'GET_CACHE_SIZE':
        handleGetCacheSize().then(size => {
          event.ports[0]?.postMessage({ cacheSize: size });
        });
        break;
    }
  }
});

// Background sync handlers

async function handleVocabularySync(): Promise<void> {
  try {
    console.log('Processing vocabulary background sync...');
    
    const queue = await vocabularySync.getQueue();
    const requests = await queue.getAll();
    
    for (const { request } of requests) {
      try {
        const response = await fetch(request.clone());
        if (response.ok) {
          // Remove from queue on success
          await queue.replayRequest(request);
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Failed to sync vocabulary item:', error);
        // Item remains in queue for retry
      }
    }
  } catch (error) {
    console.error('Vocabulary sync failed:', error);
  }
}

async function handleAnalyticsSync(): Promise<void> {
  try {
    console.log('Processing analytics background sync...');
    
    const queue = await analyticsSync.getQueue();
    const requests = await queue.getAll();
    
    for (const { request } of requests) {
      try {
        const response = await fetch(request.clone());
        if (response.ok) {
          await queue.replayRequest(request);
        }
      } catch (error) {
        console.error('Failed to sync analytics:', error);
      }
    }
  } catch (error) {
    console.error('Analytics sync failed:', error);
  }
}

async function handleSessionSync(): Promise<void> {
  try {
    console.log('Processing session background sync...');
    
    const queue = await sessionSync.getQueue();
    const requests = await queue.getAll();
    
    for (const { request } of requests) {
      try {
        const response = await fetch(request.clone());
        if (response.ok) {
          await queue.replayRequest(request);
        }
      } catch (error) {
        console.error('Failed to sync session:', error);
      }
    }
  } catch (error) {
    console.error('Session sync failed:', error);
  }
}

// Helper functions

async function handleCacheNewRoute(url: string): Promise<void> {
  try {
    const cache = await caches.open('pages-v1');
    await cache.add(url);
    console.log(`Cached new route: ${url}`);
  } catch (error) {
    console.error('Failed to cache route:', error);
  }
}

async function handleQueueSync(data: any, syncType: string): Promise<void> {
  try {
    let queue;
    switch (syncType) {
      case 'vocabulary':
        queue = vocabularySync;
        break;
      case 'analytics':
        queue = analyticsSync;
        break;
      case 'session':
        queue = sessionSync;
        break;
      default:
        console.warn('Unknown sync type:', syncType);
        return;
    }

    // Create request for the data
    const request = new Request('/api/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    await queue.pushRequest({ request });
    console.log(`Queued ${syncType} data for background sync`);
  } catch (error) {
    console.error('Failed to queue sync:', error);
  }
}

async function handleClearCache(cacheName?: string): Promise<void> {
  try {
    if (cacheName) {
      await caches.delete(cacheName);
      console.log(`Cleared cache: ${cacheName}`);
    } else {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(name => caches.delete(name))
      );
      console.log('Cleared all caches');
    }
    
    // Notify clients
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'CACHE_CLEARED',
        cacheName: cacheName || 'all'
      });
    });
  } catch (error) {
    console.error('Failed to clear cache:', error);
  }
}

async function handleGetCacheSize(): Promise<number> {
  try {
    let totalSize = 0;
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const keys = await cache.keys();
      
      for (const request of keys) {
        const response = await cache.match(request);
        if (response) {
          const blob = await response.blob();
          totalSize += blob.size;
        }
      }
    }
    
    return totalSize;
  } catch (error) {
    console.error('Failed to calculate cache size:', error);
    return 0;
  }
}

// Periodic cleanup
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'cache-cleanup') {
    event.waitUntil(performCacheCleanup());
  }
});

async function performCacheCleanup(): Promise<void> {
  try {
    const cacheNames = await caches.keys();
    const oldCaches = cacheNames.filter(name => 
      !name.includes('-v1') && name !== 'workbox-precache'
    );
    
    await Promise.all(
      oldCaches.map(cacheName => caches.delete(cacheName))
    );
    
    console.log('Cache cleanup completed');
  } catch (error) {
    console.error('Cache cleanup failed:', error);
  }
}

// Error handler
self.addEventListener('error', (event) => {
  console.error('Service Worker error:', event.error);
});

// Unhandled rejection handler
self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker unhandled rejection:', event.reason);
});

console.log('VocabLens Service Worker loaded successfully');