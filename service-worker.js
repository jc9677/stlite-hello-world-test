const CACHE_NAME = "stlite-duckdb-cdn-v1";
const CDN_HOST = "cdn.jsdelivr.net";
const CACHED_PACKAGE_PREFIXES = [
    "/npm/@stlite/browser@1.9.1/",
    "/npm/@duckdb/duckdb-wasm@1.32.0/",
];

function isCacheableCdnRequest(request) {
    if (request.method !== "GET") {
        return false;
    }

    const url = new URL(request.url);
    return url.hostname === CDN_HOST
        && CACHED_PACKAGE_PREFIXES.some((prefix) => url.pathname.startsWith(prefix));
}

self.addEventListener("install", () => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        Promise.all([
            caches.keys().then((cacheNames) => Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => caches.delete(cacheName))
            )),
            self.clients.claim(),
        ])
    );
});

self.addEventListener("fetch", (event) => {
    if (!isCacheableCdnRequest(event.request)) {
        return;
    }

    event.respondWith(
        caches.open(CACHE_NAME).then(async (cache) => {
            const cachedResponse = await cache.match(event.request);
            if (cachedResponse) {
                return cachedResponse;
            }

            const response = await fetch(event.request);
            if (response.ok || response.type === "opaque") {
                await cache.put(event.request, response.clone());
            }
            return response;
        })
    );
});