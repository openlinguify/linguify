// Simple Service Worker for Linguify Portal
const CACHE_NAME = 'linguify-portal-v1';
const urlsToCache = [
  '/',
  '/static/src/css/main.css',
  '/static/src/js/main.js',
  '/static/images/favicon.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});