/**
 * Notification Header Management
 * Handles the notification dropdown in the header
 */

class NotificationHeader {
    constructor() {
        this.notificationsList = document.getElementById('notificationsList');
        this.notificationBadge = document.getElementById('notificationBadge');
        this.markAllReadBtn = document.getElementById('markAllReadBtn');
        this.noNotifications = document.getElementById('noNotifications');
        
        if (!this.notificationsList) {
            console.log('[NotificationHeader] Elements not found, notification header not available');
            return;
        }
        
        this.init();
    }
    
    init() {
        console.log('[NotificationHeader] Initializing...');
        
        // Load initial notifications
        this.loadNotifications();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup WebSocket for real-time updates
        this.setupWebSocket();
        
        // Refresh every 30 seconds
        setInterval(() => this.loadNotifications(), 30000);
    }
    
    setupEventListeners() {
        // Mark all as read button
        if (this.markAllReadBtn) {
            this.markAllReadBtn.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }
        
        // Refresh on dropdown show
        const notificationDropdown = document.querySelector('[data-bs-toggle="dropdown"][href="#"]');
        if (notificationDropdown) {
            notificationDropdown.addEventListener('click', () => {
                this.loadNotifications();
            });
        }
    }
    
    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('[NotificationHeader] Loaded notifications:', data);
            
            this.updateNotificationDisplay(data);
            
        } catch (error) {
            console.error('[NotificationHeader] Error loading notifications:', error);
            this.showError();
        }
    }
    
    updateNotificationDisplay(data) {
        const { unread_count = 0, notifications = [] } = data;
        
        // Update badge
        this.updateBadge(unread_count);
        
        // Update dropdown content
        this.updateDropdown(notifications, unread_count);
    }
    
    updateBadge(count) {
        if (!this.notificationBadge) return;
        
        if (count > 0) {
            this.notificationBadge.textContent = count > 99 ? '99+' : count;
            this.notificationBadge.style.display = 'inline-block';
        } else {
            this.notificationBadge.style.display = 'none';
        }
    }
    
    updateDropdown(notifications, unreadCount) {
        if (!this.notificationsList) return;
        
        // Clear existing notifications (except the "no notifications" item)
        const existingItems = this.notificationsList.querySelectorAll('.notification-item');
        existingItems.forEach(item => item.remove());
        
        if (notifications.length === 0) {
            // Show "no notifications" message
            if (this.noNotifications) {
                this.noNotifications.style.display = 'block';
            }
            if (this.markAllReadBtn) {
                this.markAllReadBtn.style.display = 'none';
            }
        } else {
            // Hide "no notifications" message
            if (this.noNotifications) {
                this.noNotifications.style.display = 'none';
            }
            
            // Show "mark all read" button if there are unread notifications
            if (this.markAllReadBtn) {
                this.markAllReadBtn.style.display = unreadCount > 0 ? 'block' : 'none';
            }
            
            // Add notifications
            notifications.forEach(notification => {
                this.addNotificationToDropdown(notification);
            });
        }
    }
    
    addNotificationToDropdown(notification) {
        const li = document.createElement('li');
        li.className = `notification-item${!notification.is_read ? ' unread' : ''}`;
        
        li.innerHTML = `
            <a class="dropdown-item notification-link" href="#" data-notification-id="${notification.id}">
                <div class="d-flex align-items-start">
                    <div class="flex-shrink-0 me-3">
                        <i class="bi ${notification.icon || 'bi-bell'} text-${notification.color || 'primary'}" 
                           style="font-size: 1.2rem;"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="fw-semibold">${this.escapeHtml(notification.title)}</div>
                        <div class="text-muted small">${this.escapeHtml(notification.message)}</div>
                        <div class="text-muted smaller mt-1">
                            <i class="bi bi-clock"></i> ${notification.time || notification.created_at}
                        </div>
                    </div>
                    ${!notification.is_read ? '<div class="flex-shrink-0"><span class="badge bg-primary rounded-pill ms-2">Nouveau</span></div>' : ''}
                </div>
            </a>
        `;
        
        // Add click handler to mark as read and handle actions
        const link = li.querySelector('.notification-link');
        link.addEventListener('click', (e) => {
            e.preventDefault();
            this.markAsRead(notification.id);
            this.handleNotificationClick(notification);
        });
        
        // Insert before "no notifications" item
        if (this.noNotifications) {
            this.notificationsList.insertBefore(li, this.noNotifications);
        } else {
            this.notificationsList.appendChild(li);
        }
    }
    
    async markAsRead(notificationId) {
        try {
            const formData = new FormData();
            formData.append('action', 'mark_read');
            formData.append('notification_id', notificationId);
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());
            
            const response = await fetch('/api/notifications/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('[NotificationHeader] Marked notification as read:', notificationId);
                    // Reload notifications to update display
                    this.loadNotifications();
                } else {
                    console.error('[NotificationHeader] Error marking notification as read:', data.error);
                }
            }
        } catch (error) {
            console.error('[NotificationHeader] Error marking notification as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const formData = new FormData();
            formData.append('action', 'mark_all_read');
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());
            
            const response = await fetch('/api/notifications/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('[NotificationHeader] Marked all notifications as read');
                    this.loadNotifications();
                } else {
                    console.error('[NotificationHeader] Error marking all as read:', data.error);
                }
            }
        } catch (error) {
            console.error('[NotificationHeader] Error marking all as read:', error);
        }
    }
    
    setupWebSocket() {
        // WebSocket temporairement désactivé pour éviter les erreurs de connexion
        // TODO: Activer quand le serveur WebSocket sera configuré
        console.log('[NotificationHeader] WebSocket disabled - using polling instead');
        return;
        
        // Code WebSocket original (désactivé)
        /*
        if (typeof WebSocket === 'undefined') {
            console.log('[NotificationHeader] WebSocket not available');
            return;
        }
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
            
            this.websocket = new WebSocket(wsUrl);
            // ... reste du code WebSocket
        } catch (error) {
            console.error('[NotificationHeader] WebSocket setup error:', error);
        }
        */
    }
    
    showError() {
        if (this.notificationsList && this.noNotifications) {
            this.noNotifications.innerHTML = `
                <i class="bi bi-exclamation-triangle mb-2 text-warning" style="font-size: 2rem;" aria-hidden="true"></i>
                <div class="text-warning">Erreur de chargement</div>
            `;
            this.noNotifications.style.display = 'block';
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    handleNotificationClick(notification) {
        // Handle notification click actions based on notification type and data
        try {
            const data = notification.data || {};

            // Handle terms and conditions notifications
            if (notification.type === 'terms' || notification.type === 'terms_update' || notification.type === 'action_required') {
                console.log('[NotificationHeader] Terms notification clicked:', notification);
                console.log('[NotificationHeader] Notification data:', data);

                // Debug: afficher toutes les données de la notification
                console.log('[NotificationHeader] Notification data:', data);
                console.log('[NotificationHeader] Action URL:', data.action_url);

                // Vérifier l'URL d'action dans les données
                if (data && data.action_url) {
                    console.log('[NotificationHeader] Redirecting to:', data.action_url);
                    window.location.href = data.action_url;
                    return;
                }

                // Vérifier si le message contient "Terms" ou "Conditions"
                const message = notification.message || '';
                const title = notification.title || '';
                if (message.toLowerCase().includes('terms') ||
                    message.toLowerCase().includes('conditions') ||
                    title.toLowerCase().includes('terms') ||
                    title.toLowerCase().includes('conditions')) {
                    // Fallback vers la page d'acceptation dans le backend
                    const backendUrl = window.location.protocol + '//' + window.location.host;
                    const termsUrl = `${backendUrl}/authentication/terms/accept/`;
                    console.log('[NotificationHeader] Fallback redirect to terms acceptance page:', termsUrl);
                    window.location.href = termsUrl;
                    return;
                }
            }

            // Handle revision reminder notifications
            if (data.action === 'start_revision' || data.reminder_type === 'daily_revision') {
                console.log('[NotificationHeader] Redirecting to revision study...');
                // Redirect to revision study page
                window.location.href = '/revision/study/';
                return;
            }

            // Handle flashcard notifications
            if (notification.type === 'flashcard') {
                console.log('[NotificationHeader] Redirecting to revision...');
                window.location.href = '/revision/';
                return;
            }

            // Add more notification types as needed
            console.log('[NotificationHeader] No specific action for notification type:', notification.type);

        } catch (error) {
            console.error('[NotificationHeader] Error handling notification click:', error);
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.notificationHeader = new NotificationHeader();
});

// Also initialize on HTMX page loads if using HTMX
document.addEventListener('htmx:afterSettle', () => {
    if (!window.notificationHeader && document.getElementById('notificationsList')) {
        window.notificationHeader = new NotificationHeader();
    }
});