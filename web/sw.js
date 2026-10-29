// Offline support: caches the whole quiz on first visit so it runs without a network.
// export_web.py replaces __VERSION__ with a hash of the site, so each deploy gets a fresh cache.
const CACHE = "saa-quiz-__VERSION__";
const FILES = ["./", "index.html", "app.js", "style.css", "data.json", "manifest.webmanifest",
  "icons/icon-180.png", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Cache first, so the app opens instantly and offline; a new deploy arrives as a new worker
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true })
    .then((hit) => hit || fetch(e.request)));
});
