/**
 * Privacy Gate Service Worker
 *
 * Caches the static shell for offline load: vault/, privacy-export/, theme/, manifest, icons.
 * Does NOT cache API responses — those require the local FastAPI server.
 * Scope: / — intercepts all requests from the PWA.
 *
 * Registration: called from vault/index.html and privacy-export/index.html
 * Path: /service-worker.js (at root, not /static/)
 */

const CACHE_NAME = 'privacy-gate-v5';
const STATIC_PATHS = [
  '/',
  '/manifest.json',
  '/vault/',
  '/vault/index.html',
  '/vault/vault.js',
  '/vault/qr.js',
  '/vault/qrcodegen.js',
  '/privacy-export/',
  '/privacy-export/index.html',
  '/privacy-export/privacy-export.js',
  '/privacy-export/demo-payload.js',
  '/privacy-export/pipeline.js',
  '/privacy-export/pipeline.css',
  '/theme/index.html',
  '/theme/tokens.js',
  '/theme/tokens.css',
  '/theme/components.css',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

/**
 * Install: cache the static shell
 */
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] caching static shell');
      return cache.addAll(STATIC_PATHS).catch((err) => {
        // Some paths may not exist yet (e.g., custom themes) — log but continue
        console.log('[ServiceWorker] cache warning:', err.message);
      });
    })
  );
  self.skipWaiting();
});

/**
 * Activate: clean up old caches
 */
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

/**
 * Fetch: cache-first for static assets, network-first for API
 */
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Do NOT cache API calls — they require the local server
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Cache-first strategy for static assets
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(event.request).then((response) => {
        // Cache successful responses for future offline access
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      });
    }).catch(() => {
      // If both cache and network fail, return a fallback
      console.log('[ServiceWorker] failed to fetch:', url.pathname);
      return new Response('Offline — unable to reach network', {
        status: 503,
        statusText: 'Service Unavailable',
      });
    })
  );
});
