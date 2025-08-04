/**
 * Notification Settings JavaScript
 * Handles notification-specific settings functionality
 */

function initializeNotificationSettings() {
    console.log('[Notification Settings] Initializing notification-specific settings...');
    
    // Master notification toggle
    const enableNotificationsToggle = document.querySelector('input[name="enable_notifications"]');
    const notificationOptions = document.querySelector('.notification-options');
    
    if (enableNotificationsToggle && notificationOptions) {
        function toggleNotificationOptions() {
            const enabled = enableNotificationsToggle.checked;
            notificationOptions.style.opacity = enabled ? '1' : '0.5';
            notificationOptions.style.pointerEvents = enabled ? 'auto' : 'none';
            
            // Disable all sub-options if master is off
            if (!enabled) {
                notificationOptions.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                    checkbox.checked = false;
                });
                showTemporaryMessage('Toutes les notifications désactivées', 'warning');
            } else {
                showTemporaryMessage('Notifications activées', 'success');
            }
        }
        
        enableNotificationsToggle.addEventListener('change', toggleNotificationOptions);
        toggleNotificationOptions(); // Initial state
    }
    
    // Browser notifications permission
    const browserNotificationsToggle = document.querySelector('input[name="browser_notifications"]');
    if (browserNotificationsToggle) {
        browserNotificationsToggle.addEventListener('change', async () => {
            if (browserNotificationsToggle.checked) {
                // Check browser support
                if (!('Notification' in window)) {
                    browserNotificationsToggle.checked = false;
                    showTemporaryMessage('Votre navigateur ne supporte pas les notifications', 'error');
                    return;
                }
                
                // Request permission
                if (Notification.permission === 'default') {
                    const permission = await Notification.requestPermission();
                    if (permission !== 'granted') {
                        browserNotificationsToggle.checked = false;
                        showTemporaryMessage('Permission refusée pour les notifications', 'warning');
                    } else {
                        showTemporaryMessage('Notifications du navigateur activées', 'success');
                        // Show test notification
                        new Notification('Linguify', {
                            body: 'Les notifications sont maintenant activées!',
                            icon: '/static/images/icon-192.png'
                        });
                    }
                } else if (Notification.permission === 'denied') {
                    browserNotificationsToggle.checked = false;
                    showTemporaryMessage('Les notifications sont bloquées dans votre navigateur', 'error');
                }
            } else {
                showTemporaryMessage('Notifications du navigateur désactivées', 'info');
            }
        });
    }
    
    // Notification types
    const notificationTypes = [
        { name: 'lesson_reminders', label: 'Rappels de leçons' },
        { name: 'achievement_notifications', label: 'Succès et récompenses' },
        { name: 'friend_activity', label: 'Activité des amis' },
        { name: 'message_notifications', label: 'Messages' },
        { name: 'streak_reminders', label: 'Rappels de série' },
        { name: 'weekly_progress', label: 'Progrès hebdomadaire' }
    ];
    
    notificationTypes.forEach(type => {
        const checkbox = document.querySelector(`input[name="${type.name}"]`);
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                const status = checkbox.checked ? 'activées' : 'désactivées';
                showTemporaryMessage(`${type.label} ${status}`, 'info');
            });
        }
    });
    
    // Quiet hours
    const quietHoursToggle = document.querySelector('input[name="enable_quiet_hours"]');
    const quietHoursConfig = document.querySelector('.quiet-hours-config');
    
    if (quietHoursToggle && quietHoursConfig) {
        function toggleQuietHours() {
            quietHoursConfig.style.display = quietHoursToggle.checked ? 'block' : 'none';
            if (quietHoursToggle.checked) {
                showTemporaryMessage('Heures silencieuses activées', 'info');
            }
        }
        
        quietHoursToggle.addEventListener('change', toggleQuietHours);
        toggleQuietHours(); // Initial state
    }
    
    // Time validation for quiet hours
    const quietStartInput = document.querySelector('input[name="quiet_hours_start"]');
    const quietEndInput = document.querySelector('input[name="quiet_hours_end"]');
    
    if (quietStartInput && quietEndInput) {
        function validateQuietHours() {
            const start = quietStartInput.value;
            const end = quietEndInput.value;
            
            if (start && end) {
                showTemporaryMessage(`Heures silencieuses: ${start} - ${end}`, 'info');
            }
        }
        
        quietStartInput.addEventListener('change', validateQuietHours);
        quietEndInput.addEventListener('change', validateQuietHours);
    }
    
    console.log('[Notification Settings] Notification settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeNotificationSettings();
});