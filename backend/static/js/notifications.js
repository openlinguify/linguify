// Global notification service for Linguify
window.notificationService = {
    success: function(message) {
        this.show(message, 'success');
    },
    
    error: function(message) {
        this.show(message, 'error');
    },
    
    info: function(message) {
        this.show(message, 'info');
    },
    
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    show: function(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => {
            notification.remove();
        });

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close ms-2" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
};

// CSS styles for notifications
const notificationStyles = `
.notification {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 2000;
    max-width: 400px;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    transition: all 0.3s ease;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.notification.success {
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    color: #166534;
}

.notification.error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #dc2626;
}

.notification.info {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}

.notification.warning {
    background: #fef3c7;
    border: 1px solid #fde68a;
    color: #92400e;
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

console.log('Notification service loaded');