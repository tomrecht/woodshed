// Offline cache. Serves cached files instantly, refreshes them in the background.
const CACHE = 'woodshed-v20';
const FILES = ['./', 'index.html', 'library.json', 'manifest.json', 'icon-192.png', 'icon-512.png', ...Array.from({ length: 25 }, (_, i) => `licks/lick-${i + 1}.png`),
  ...['C1','Ds1','Fs1','A1','C2','Ds2','Fs2','A2','C3','Ds3','Fs3','A3','C4','Ds4','Fs4','A4','C5','Ds5','Fs5'].map(n => `piano/${n}.mp3`),
  ...['ride1', 'ride2', 'hat1', 'hat2', 'kick'].map(n => `drums/${n}.mp3`)];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(e.request, { ignoreSearch: true });
    const net = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => hit);
    return hit || net;
  }));
});
