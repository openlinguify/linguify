# Notification System Testing Guide

This document provides guidance on how to test and debug the Linguify notification system, including WebSocket real-time notifications, browser notifications, and our enhanced frontend notification testing utilities.

## Setup Requirements

Before testing the notification system, make sure you have the following components running:

1. **Redis Server** - Required for WebSocket communication:
   ```bash
   docker-compose -f docker-compose.redis.yml up -d
   ```

2. **Django Backend**:
   ```bash
   cd backend
   python manage.py runserver
   ```

3. **Frontend Application**:
   ```bash
   cd frontend
   npm run dev
   ```

## Testing Real-time Notifications

The Linguify notification system supports real-time notifications via WebSockets. Here's how to test it:

### Using the Test Script

A comprehensive test script is provided at `backend/test_notification_websocket.py`:

```bash
# Default - sends to user ID 1 (admin)
python test_notification_websocket.py

# Specify a different user ID
python test_notification_websocket.py 2
```

This script will:
- Clean up old notifications for the user
- Create one of each type of notification (system, lesson reminder, flashcard reminder, achievement, streak)
- Send them in real-time via WebSockets

### Manual Testing with Python Shell

You can also test notifications manually using the Django shell:

```bash
python manage.py shell
```

```python
from apps.notification.utils import NotificationManager
from apps.notification.models import NotificationType, NotificationPriority
from apps.authentication.models import User

# Get a user
user = User.objects.get(id=1)  # Change ID as needed

# Create and send a notification
notification = NotificationManager.create_notification(
    user=user,
    title="Test Notification",
    message="This is a test notification from the shell",
    notification_type=NotificationType.INFO,
    priority=NotificationPriority.HIGH,
    data={"test": True},
    send_realtime=True
)

print(f"Created notification with ID: {notification.id}")
```

## Verifying Notification Delivery

### WebSocket Connection

To verify that WebSocket connections are working properly:

1. Open your browser's developer tools (F12)
2. Go to the "Network" tab
3. Filter by "WS" to see WebSocket connections
4. Look for a connection to `/ws/notifications/`
5. The connection should show as "open" (green)

### Notification Receipt

When a notification is sent:

1. You should see a notification appear in the notification dropdown in the UI
2. For high-priority notifications, a toast notification should appear
3. If browser notifications are enabled, a browser notification should appear

### Backend Logs

Check the Django server logs for WebSocket activity:

```
[11/May/2025 01:07:46] User 1 connected to notification WebSocket
[11/May/2025 01:07:46] Notification WebSocket connected
```

## Debugging Common Issues

### WebSocket Connection Issues

If WebSocket connections are failing:

1. **Check Redis is running**:
   ```bash
   docker ps | grep redis
   ```

2. **Verify ASGI configuration**:
   - Check `backend/core/asgi.py` to ensure notification routing is included
   - Verify `CHANNEL_LAYERS` settings in `settings.py`

3. **Check for WebSocket errors in browser console**:
   - Look for connection errors in the Console tab of developer tools

### Notification Not Appearing

If notifications are created but not appearing in the UI:

1. **Check notification database records**:
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.notification.models import Notification
   Notification.objects.filter(user_id=1).order_by('-created_at')[:5].values()
   ```

2. **Verify WebSocket message format**:
   - Use browser developer tools to inspect WebSocket frames
   - WebSocket messages should have the format:
     ```json
     {
       "type": "notification",
       "notification": {
         "id": "...",
         "type": "...",
         "title": "...",
         "message": "...",
         "priority": "...",
         "data": {},
         "is_read": false,
         "created_at": "...",
         "expires_at": null
       }
     }
     ```

3. **Check notification permissions**:
   - Browser notifications require permission from the user
   - Check permission status in browser console: `Notification.permission`

## Extending the Notification System

To add a new notification type:

1. Add the new type to `NotificationType` enum in both:
   - Backend: `backend/apps/notification/models.py`
   - Frontend: `frontend/src/core/types/notification.types.ts`

2. Add a helper method in `NotificationManager` (backend) to create this type of notification

3. Add a corresponding method in the frontend notification context and service

## Browser Notification Support

Browser notifications require user permission. To test:

1. Click the bell icon in the UI
2. If permission is not granted, a banner will appear asking for permission
3. Click "Enable Notifications" to request permission
4. Send a high-priority notification to test browser notification

## Frontend Testing Utilities

Linguify provides a comprehensive frontend testing utility for creating and testing notifications without requiring backend integration.

### Test Notification Panel

The **Test Notification Panel** is a component that provides an easy way to create test notifications through the UI. It's automatically available in the dashboard header when the app is running in development mode.

To use it:

1. Run the frontend in development mode (`npm run dev`)
2. Log in to access the dashboard
3. Click on the "Test Notifications" button in the header
4. Choose from two testing modes:
   - **Enhanced System** - For creating notifications via the NotificationContext
   - **Legacy System** - For creating notifications via localStorage (for backward compatibility)

### Enhanced Notification Types

The enhanced system supports the following notification types:

- **Lesson Reminder** - Notifications about continuing lessons
- **System Notification** - Important system updates and messages
- **Achievement Notification** - User achievements and milestones
- **Study Reminder** - General study reminders
- **Flashcard Notification** - Reminders about flashcard practice
- **Announcement** - New features and important announcements

You can create individual notifications or generate all types at once with the "Create All Notification Types" option.

### Legacy Notification Types

The legacy system supports various lesson notification types:

- **Vocabulary Lesson**
- **Numbers Game**
- **Theory Lesson**
- **Unit Lesson**
- **Fill Blank Exercise**

### Programmatic Testing

If you need to test notifications programmatically, you can use the utilities in `frontend/src/core/test-notification-system.ts`:

```typescript
import {
  createTestNotification,
  createAllTestNotifications
} from '@/core/test-notification-system';
import { NotificationType } from '@/core/types/notification.types';

// Create a specific notification type
const notification = createTestNotification(NotificationType.LESSON_REMINDER);

// Create all notification types
const allNotifications = createAllTestNotifications();
```

## Performance Considerations

- The system is designed to handle multiple concurrent connections
- Redis provides scalability for WebSocket communication
- For testing high loads, consider using a tool like [websocket-bench](https://github.com/M6Web/websocket-bench)
- The frontend notification context is optimized to handle large numbers of notifications efficiently