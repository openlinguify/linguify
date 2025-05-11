// Service Worker for Push Notifications
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing Service Worker...', event);
  self.skipWaiting(); // Ensure service worker is activated immediately
});

self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating Service Worker...', event);
  return self.clients.claim(); // Take control of all clients
});

// Handle incoming push notifications
self.addEventListener('push', event => {
  console.log('[Service Worker] Push notification received:', event);

  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      console.error('[Service Worker] Error parsing push data:', e);
      data = {
        title: 'New Notification',
        message: event.data.text(),
        icon: '/logo/logo.png',
        badge: '/logo/logo.png'
      };
    }
  }

  // Set defaults if data is missing properties
  const title = data.title || 'Linguify Notification';
  const options = {
    body: data.message || 'You have a new notification',
    icon: data.icon || '/logo/logo.png',
    badge: data.badge || '/logo/logo.png',
    tag: data.id || 'default',
    data: {
      url: data.url || '/',
      notificationId: data.id,
      ...data.data
    },
    actions: data.actions || [],
    requireInteraction: data.requireInteraction || false,
    silent: data.silent || false,
    renotify: data.renotify || false,
    timestamp: data.timestamp || Date.now()
  };

  // Show the notification
  const showNotificationPromise = self.registration.showNotification(title, options);
  event.waitUntil(showNotificationPromise);
});

// Handle notification click
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification click received:', event);

  // Close the notification
  event.notification.close();

  // Extract URL from notification data
  const url = event.notification.data?.url || '/';
  const notificationId = event.notification.data?.notificationId;
  
  // Handle action clicks
  let actionUrl = url;
  if (event.action) {
    // Find the corresponding action in the notification
    const action = event.notification.data?.actions?.find(a => a.id === event.action);
    if (action && action.url) {
      actionUrl = action.url;
    }
  }

  // Mark notification as read if we have a notificationId
  if (notificationId) {
    // This is a good place to call an API to mark the notification as read
    // Placeholder for future implementation
    console.log('[Service Worker] Should mark notification as read:', notificationId);
  }

  // Focus if already open, or open new window
  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(clientsList => {
      // Check if a window is already open
      for (const client of clientsList) {
        if (client.url === actionUrl && 'focus' in client) {
          return client.focus();
        }
      }
      
      // If no matching window, open a new one
      if (clients.openWindow) {
        return clients.openWindow(actionUrl);
      }
    })
  );
});

// Listen for messages from the client
self.addEventListener('message', event => {
  console.log('[Service Worker] Message received:', event.data);
  
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});