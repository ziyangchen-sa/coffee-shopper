// Minimal service worker: cache the app shell so it installs + works offline,
// but always go to the network first for the live product feed.
const CACHE = 'hydrangea-v4';
const SHELL = [
  '.', 'index.html', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);

  // Network-first for the HTML page itself and the live catalog, so updates
  // (new app versions, new coffees) show immediately when online — falling
  // back to the last cached copy only when offline.
  const isHTML = e.request.mode === 'navigate' ||
    url.origin === location.origin && (url.pathname === '/' || url.pathname.endsWith('/') || url.pathname.endsWith('index.html'));
  const isFeed = url.hostname === 'hydrangea.coffee' && url.pathname.endsWith('products.json');
  if (isHTML || isFeed) {
    e.respondWith(
      fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match(e.request).then(hit => hit || caches.match('index.html')))
    );
    return;
  }

  // Everything else (app shell, Shopify product images): cache-first, then network.
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok && (url.hostname === 'cdn.shopify.com' || url.origin === location.origin)) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return res;
    }))
  );
});
