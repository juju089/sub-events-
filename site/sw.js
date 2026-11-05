'use strict';
const CACHE = 'sub-shell-v1';
const ROOT = new URL('./', self.location).href;
const SHELL = ['./', './index.html', './style.css', './calendar.js', './app.js', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener('activate', event => { event.waitUntil((async () => { for (const key of await caches.keys()) if (key.startsWith('sub-') && key !== CACHE) await caches.delete(key); await self.clients.claim(); })()); });
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || !url.href.startsWith(ROOT) || url.origin !== self.location.origin) return;
  // Calendar subscribers always get the actual server response, never a hidden stale cache.
  if (url.pathname.endsWith('.ics')) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const response = await fetch(event.request);
      if (!response.ok) throw Error('HTTP ' + response.status);
      await cache.put(event.request, response.clone()); return response;
    } catch {
      const cached = await cache.match(event.request);
      if (cached) return cached;
      if (event.request.mode === 'navigate') return (await cache.match(new URL('./index.html', ROOT))) || Response.error();
      return Response.error();
    }
  })());
});
