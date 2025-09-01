/// <reference types="@sveltejs/kit" />
import { build, files, version } from '$service-worker';

// Create a unique cache name for this deployment
const CACHE = `cache-${version}`;

// Assets to cache on install
const ASSETS = [
	...build, // the app itself
	...files  // static files
];

// Service worker install event
self.addEventListener('install', (event) => {
	// Create a new cache and add all files to it
	async function addFilesToCache() {
		const cache = await caches.open(CACHE);
		await cache.addAll(ASSETS);
	}

	event.waitUntil(addFilesToCache());
});

// Service worker activate event
self.addEventListener('activate', (event) => {
	// Remove previous cached data from disk
	async function deleteOldCaches() {
		for (const key of await caches.keys()) {
			if (key !== CACHE) {
				await caches.delete(key);
			}
		}
	}

	event.waitUntil(deleteOldCaches());
});

// Service worker fetch event
self.addEventListener('fetch', (event) => {
	// Ignore POST requests etc
	if (event.request.method !== 'GET') return;

	async function respond() {
		const url = new URL(event.request.url);
		const cache = await caches.open(CACHE);

		// `build`/`files` can always be served from the cache
		if (ASSETS.includes(url.pathname)) {
			const response = await cache.match(url.pathname);
			if (response) {
				return response;
			}
		}

		// For everything else, try the network first, but
		// fall back to the cache if we're offline
		try {
			const response = await fetch(event.request);

			// If we're offline, fetch can return a response with status 0
			if (!(response instanceof Response)) {
				throw new Error('invalid response from fetch');
			}

			if (response.status === 200) {
				cache.put(event.request, response.clone());
			}

			return response;
		} catch (err) {
			const response = await cache.match(event.request);

			if (response) {
				return response;
			}

			// If there's no cache, return a generic offline page
			if (url.pathname === '/' || url.pathname.includes('.html')) {
				const fallbackResponse = await cache.match('/');
				if (fallbackResponse) {
					return fallbackResponse;
				}
			}

			throw err;
		}
	}

	event.respondWith(respond());
});

// Handle background sync for form submissions when offline
self.addEventListener('sync', (event) => {
	if (event.tag === 'background-sync') {
		event.waitUntil(doBackgroundSync());
	}
});

async function doBackgroundSync() {
	// Handle any queued actions when back online
	console.log('Background sync triggered');
}

// Handle push notifications if implemented
self.addEventListener('push', (event) => {
	const options = {
		body: event.data?.text() ?? 'New notification',
		icon: '/favicon-32x32.png',
		badge: '/favicon-32x32.png',
		vibrate: [100, 50, 100],
		data: {
			dateOfArrival: Date.now(),
			primaryKey: '1'
		}
	};

	event.waitUntil(
		self.registration.showNotification('Portfolio Update', options)
	);
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
	event.notification.close();

	event.waitUntil(
		clients.matchAll().then((clientList) => {
			if (clientList.length > 0) {
				return clientList[0].focus();
			}
			return clients.openWindow('/');
		})
	);
});

// Performance monitoring
self.addEventListener('message', (event) => {
	if (event.data?.type === 'SKIP_WAITING') {
		self.skipWaiting();
	}
});

// Cache strategies for different types of resources
const cacheStrategies = {
	// Static assets - cache first
	static: async (request: Request) => {
		const cache = await caches.open(CACHE);
		const cached = await cache.match(request);
		return cached || fetch(request);
	},

	// API calls - network first with cache fallback
	api: async (request: Request) => {
		const cache = await caches.open(CACHE);
		try {
			const response = await fetch(request);
			if (response.ok) {
				cache.put(request, response.clone());
			}
			return response;
		} catch {
			return cache.match(request) || new Response('Offline', { status: 503 });
		}
	},

	// Images - cache first with network fallback
	images: async (request: Request) => {
		const cache = await caches.open(CACHE);
		const cached = await cache.match(request);
		if (cached) return cached;

		try {
			const response = await fetch(request);
			if (response.ok) {
				cache.put(request, response.clone());
			}
			return response;
		} catch {
			// Return a placeholder image if offline
			return new Response('', { status: 503 });
		}
	}
};