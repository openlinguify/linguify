// Système de notifications pour Open Linguify

// Notification system
function loadNotifications() {
    fetch('/api/notifications/')
        .then(response => response.json())
        .then(data => {
            const notificationsList = document.getElementById('notificationsList');
            const notificationBadge = document.getElementById('notificationBadge');
            const markAllReadBtn = document.getElementById('markAllReadBtn');
            const noNotifications = document.getElementById('noNotifications');
            
            // Update badge
            if (data.unread_count > 0) {
                notificationBadge.textContent = data.unread_count;
                notificationBadge.style.display = 'block';
                markAllReadBtn.style.display = 'block';
                noNotifications.style.display = 'none';
            } else {
                notificationBadge.style.display = 'none';
                markAllReadBtn.style.display = 'none';
                noNotifications.style.display = 'block';
            }
            
            // Clear existing notifications except header and no-notifications message
            const existingItems = notificationsList.querySelectorAll('li:not(:first-child):not(#noNotifications)');
            existingItems.forEach(item => item.remove());
            
            // Add notifications
            data.notifications.forEach(notification => {
                const li = document.createElement('li');
                li.className = 'border-bottom notification-item';
                li.setAttribute('data-id', notification.id);
                
                // Handle terms notification click
                let clickAction = '';
                if (notification.type === 'terms' && notification.data.terms_url) {
                    clickAction = `onclick="handleTermsNotification('${notification.id}', '${notification.data.terms_url}')"`;
                } else {
                    clickAction = `onclick="markNotificationRead('${notification.id}')"`;
                }
                
                li.innerHTML = `
                    <div class="p-3 notification-content" ${clickAction} style="cursor: pointer;">
                        <div class="d-flex align-items-start">
                            <div class="me-3">
                                <i class="bi ${notification.icon} text-${notification.color}" style="font-size: 1.2rem;"></i>
                            </div>
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-start mb-1">
                                    <h6 class="mb-0 fw-bold">${notification.title}</h6>
                                    <small class="text-muted">${notification.time}</small>
                                </div>
                                <p class="mb-1 text-muted small">${notification.message}</p>
                                ${notification.priority === 'high' ? '<span class="badge bg-danger">Urgent</span>' : ''}
                            </div>
                            <button class="btn btn-sm btn-outline-secondary ms-2" onclick="event.stopPropagation(); markNotificationRead('${notification.id}')" title="Marquer comme lu">
                                <i class="bi bi-check"></i>
                            </button>
                        </div>
                    </div>
                `;
                
                notificationsList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des notifications:', error);
        });
}

function markNotificationRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the notification from the list
            const notificationItem = document.querySelector(`[data-id="${notificationId}"]`);
            if (notificationItem) {
                notificationItem.remove();
            }
            
            // Reload notifications to update count
            loadNotifications();
        }
    })
    .catch(error => {
        console.error('Erreur lors de la mise à jour de la notification:', error);
    });
}

function handleTermsNotification(notificationId, termsUrl) {
    // Mark as read first
    markNotificationRead(notificationId);
    
    // Navigate to terms page (same tab)
    window.location.href = termsUrl || '/annexes/terms/';
}

function markAllNotificationsRead() {
    fetch('/api/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadNotifications();
        }
    })
    .catch(error => {
        console.error('Erreur lors de la mise à jour des notifications:', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize notifications when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Load notifications
    loadNotifications();
    
    // Event listener for mark all read button
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllNotificationsRead);
    }
    
    // Refresh notifications every 30 seconds
    setInterval(loadNotifications, 30000);
});

// Export functions for use in other scripts
window.notificationSystem = {
    load: loadNotifications,
    markRead: markNotificationRead,
    markAllRead: markAllNotificationsRead,
    handleTerms: handleTermsNotification
};