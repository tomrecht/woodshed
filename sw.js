// Offline cache. The page is fetched fresh when online; other files are served from the cache and refreshed in the background.
const CACHE = 'woodshed-v112';
const FILES = ['./', 'index.html', 'vendor/abcjs-basic-min.js', 'library.json', 'fingerings.json', 'manifest.json', 'icon-192.png', 'icon-512.png', ...Array.from({ length: 25 }, (_, i) => `licks/lick-${i + 1}.png`),
  ...['C1','Ds1','Fs1','A1','C2','Ds2','Fs2','A2','C3','Ds3','Fs3','A3','C4','Ds4','Fs4','A4','C5','Ds5','Fs5'].map(n => `piano/${n}.mp3`),
  ...['ride1', 'ride2', 'hat1', 'hat2', 'kick'].map(n => `drums/${n}.mp3`)];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  // The app page itself: network first (so an update shows on the first open), the cached copy if offline or slow (>4 s)
  const u = new URL(e.request.url);
  if (e.request.mode === 'navigate' || u.pathname.endsWith('/') || u.pathname.endsWith('/index.html')) {
    e.respondWith(caches.open(CACHE).then(async c => {
      const hit = () => c.match(e.request, { ignoreSearch: true }).then(h => h || c.match('index.html'));
      try {
        const r = await Promise.race([fetch(e.request, { cache: 'no-store' }), new Promise((_, rej) => setTimeout(() => rej(new Error('slow')), 4000))]);
        if (r.ok) { c.put(e.request, r.clone()); return r; }
        return (await hit()) || r;
      } catch (err) { return (await hit()) || Response.error(); }
    }));
    return;
  }
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(e.request, { ignoreSearch: true });
    const net = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => hit);
    return hit || net;
  }));
});
