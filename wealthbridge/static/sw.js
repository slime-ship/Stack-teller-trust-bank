

const CACHE_NAME = 'stackteller-v1.0.0';
const STATIC_ASSETS = [
  '/',
  // Original and all resized icons
  '/static/images/blue.png',
  '/static/images/blue-16x16.png',
  '/static/images/blue-32x32.png',
  '/static/images/blue-72x72.png',
  '/static/images/blue-96x96.png',
  '/static/images/blue-128x128.png',
  '/static/images/blue-144x144.png',
  '/static/images/blue-152x152.png',
  '/static/images/blue-180x180.png',
  '/static/images/blue-192x192.png',
  '/static/images/blue-384x384.png',
  '/static/images/blue-512x512.png',
  '/static/images/favicon.ico',
  '/static/images/blue-screenshot.png',
  // Other assets
  '/static/css/dash.css',
  '/static/js/main.js',
  '/manifest.json',
  '/offline/'
];

// Update fallback images to use standard 192x192 size
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    console.log('[Service Worker] Serving from cache:', request.url);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone()).catch(error => {
        console.warn('[Service Worker] Failed to cache response:', error);
      });
    }
    
    return networkResponse;
  } catch (error) {
    console.warn('[Service Worker] Network failed, no cache available:', request.url);
    
    // Return appropriate fallback - use 192x192 for images fallback
    if (request.destination === 'images') {
      return caches.match('/static/images/blue-192x192.png');
    }
    
    if (request.headers.get('accept')?.includes('text/html')) {
      return caches.match('/offline/');
    }
    
    return new Response('Offline', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Update push notifications to use 192x192 icon
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  
  const options = {
    body: data.body || 'New update from Stack Teller Trust Bank',
    icon: '/static/images/blue-192x192.png',  // Updated
    badge: '/static/images/blue-192x192.png',  // Updated
    images: '/static/images/blue-192x192.png',  // Updated
    vibrate: [200, 100, 200],
    data: {
      url: data.url || '/',
      timestamp: Date.now()
    },
    actions: [
      {
        action: 'open',
        title: 'Open App',
        icon: '/static/images/blue-96x96.png'  // Updated
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/static/images/blue-96x96.png'  // Updated
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Stack Teller Trust Bank', options)
  );
});
