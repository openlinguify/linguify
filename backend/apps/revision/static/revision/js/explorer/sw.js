// Linguify Explorer Service Worker
const CACHE_NAME = 'linguify-explorer-v1';
const STATIC_CACHE = 'linguify-static-v1';
const API_CACHE = 'linguify-api-v1';

// Resources to cache on install
const STATIC_RESOURCES = [
    '/static/revision/js/revision-explore.js',
    '/static/revision/images/explore-hero.webp',
    '/static/revision/images/community-icon.svg',
    '/static/bootstrap/css/bootstrap.min.css',
    '/static/bootstrap/js/bootstrap.bundle.min.js'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    /\/api\/v1\/revision\/public\/stats\//,
    /\/api\/v1\/revision\/public\/trending\//,
    /\/api\/v1\/revision\/public\/popular\//,
    /\/api\/v1\/notifications\//
];

// Install event - cache static resources
self.addEventListener('install', event => {
    event.waitUntil(
        Promise.all([
            caches.open(STATIC_CACHE).then(cache => {
                return cache.addAll(STATIC_RESOURCES.filter(url => !url.includes('undefined')));
            }),
            caches.open(API_CACHE)
        ]).then(() => {
            console.log('💾 Service Worker: Static resources cached');
            self.skipWaiting();
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name !== STATIC_CACHE && name !== API_CACHE)
                    .map(name => caches.delete(name))
            );
        }).then(() => {
            console.log('🧹 Service Worker: Old caches cleaned');
            self.clients.claim();
        })
    );
});

// Fetch event - serve from cache with fallback strategies
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;
    
    // Skip cross-origin requests
    if (url.origin !== location.origin) return;
    
    // Handle different types of requests
    if (isStaticResource(url.pathname)) {
        event.respondWith(cacheFirstStrategy(event.request));
    } else if (isAPIRequest(url.pathname)) {
        event.respondWith(networkFirstStrategy(event.request));
    } else if (isHTML(url.pathname)) {
        event.respondWith(networkFirstStrategy(event.request));
    }
});

// Cache-first strategy for static resources
async function cacheFirstStrategy(request) {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            // Serve from cache, update in background
            fetch(request).then(response => {
                if (response.ok) {
                    cache.put(request, response.clone());
                }
            }).catch(error => console.log('Background update failed:', error));
            
            return cachedResponse;
        }
        
        // Not in cache, fetch and cache
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
        
    } catch (error) {
        console.error('Cache-first strategy failed:', error);
        return new Response('Offline content unavailable', { status: 503 });
    }
}

// Network-first strategy for API and dynamic content
async function networkFirstStrategy(request) {
    try {
        const response = await fetch(request);
        
        if (response.ok && isAPIRequest(request.url)) {
            // Cache successful API responses with TTL
            const cache = await caches.open(API_CACHE);
            const responseClone = response.clone();
            
            // Add timestamp for TTL
            const responseWithTTL = new Response(responseClone.body, {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers: {
                    ...responseClone.headers,
                    'sw-cached-at': Date.now()
                }
            });
            
            cache.put(request, responseWithTTL);
        }
        
        return response;
        
    } catch (error) {
        // Network failed, try cache
        if (isAPIRequest(request.url)) {
            const cache = await caches.open(API_CACHE);
            const cachedResponse = await cache.match(request);
            
            if (cachedResponse) {
                // Check TTL (5 minutes for API responses)
                const cachedAt = cachedResponse.headers.get('sw-cached-at');
                if (cachedAt && (Date.now() - cachedAt < 5 * 60 * 1000)) {
                    return cachedResponse;
                }
            }
        }
        
        console.error('Network-first strategy failed:', error);
        return new Response(
            JSON.stringify({ error: 'Offline', cached: false }), 
            { 
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

// Helper functions
function isStaticResource(pathname) {
    return /\.(css|js|png|jpg|jpeg|gif|webp|svg|woff|woff2|ttf)$/i.test(pathname);
}

function isAPIRequest(url) {
    return API_CACHE_PATTERNS.some(pattern => pattern.test(url));
}

function isHTML(pathname) {
    return !pathname.includes('.') || pathname.endsWith('.html');
}

// Background sync for analytics
self.addEventListener('sync', event => {
    if (event.tag === 'analytics-sync') {
        event.waitUntil(syncAnalytics());
    }
});

async function syncAnalytics() {
    try {
        // Get stored analytics data
        const analyticsData = await getStoredAnalytics();
        
        if (analyticsData.length > 0) {
            // Send to server
            await fetch('/api/v1/analytics/batch/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ events: analyticsData })
            });
            
            // Clear stored data after successful sync
            await clearStoredAnalytics();
            console.log('📊 Analytics synced:', analyticsData.length, 'events');
        }
    } catch (error) {
        console.error('Analytics sync failed:', error);
    }
}

// IndexedDB helpers for analytics storage
async function getStoredAnalytics() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('LinguifyAnalytics', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['events'], 'readonly');
            const store = transaction.objectStore('events');
            const getAll = store.getAll();
            
            getAll.onsuccess = () => resolve(getAll.result || []);
            getAll.onerror = () => reject(getAll.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function clearStoredAnalytics() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('LinguifyAnalytics', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['events'], 'readwrite');
            const store = transaction.objectStore('events');
            const clear = store.clear();
            
            clear.onsuccess = () => resolve();
            clear.onerror = () => reject(clear.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

// Notification handlers
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    // Handle notification click
    event.waitUntil(
        self.clients.openWindow('/explorer/').then(client => {
            if (client) {
                client.postMessage({
                    type: 'notification_clicked',
                    data: event.notification.data
                });
            }
        })
    );
});

// Push notification handler
self.addEventListener('push', event => {
    const options = {
        body: 'Nouveaux decks disponibles!',
        icon: '/static/revision/images/notification-icon.png',
        badge: '/static/revision/images/badge-icon.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Explorer',
                icon: '/static/revision/images/action-explore.png'
            },
            {
                action: 'close',
                title: 'Fermer',
                icon: '/static/revision/images/action-close.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Linguify Explorer', options)
    );
});

console.log('🚀 Linguify Explorer Service Worker loaded');