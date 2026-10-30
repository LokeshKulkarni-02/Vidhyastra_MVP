const CACHE = 'vidhyastra-static-v1';
const ASSETS = ['/static/style.css', '/static/app.js', '/manifest.json'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  // Cache only static, non-personal assets. Never cache authenticated dashboards or student data.
  if (url.origin === self.location.origin && (url.pathname.startsWith('/static/') || url.pathname === '/manifest.json')) {
    event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
      if (response.ok) caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
      return response;
    })));
  }
});
