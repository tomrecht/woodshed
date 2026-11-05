// Limber moved to /limber/. This worker only removes itself; it deletes no caches (the origin is shared).
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', () => self.registration.unregister());
