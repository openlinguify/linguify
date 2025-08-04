// Dashboard JavaScript functionality

// Variables globales pour le chat - récupérées depuis les data attributes
window.currentUserId = null;
window.currentUsername = '';
window.csrfToken = '';

// Initialize chat variables from data attributes
function initializeChatVariables() {
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        const userId = contentArea.getAttribute('data-user-id');
        const username = contentArea.getAttribute('data-username');
        const csrfToken = contentArea.getAttribute('data-csrf-token');
        
        if (userId && userId !== 'null') {
            window.currentUserId = parseInt(userId);
            window.currentUsername = username || '';
            window.csrfToken = csrfToken || '';
            console.log('[Dashboard] Variables chat définies - userId:', window.currentUserId, 'username:', window.currentUsername);
        }
    }
}

// Apply app icon gradients from data attributes
document.addEventListener('DOMContentLoaded', function () {
    // Initialize chat variables first
    initializeChatVariables();
    const appIcons = document.querySelectorAll('.app-icon[data-gradient], .app-icon-simple[data-gradient]');
    appIcons.forEach(icon => {
        const gradient = icon.getAttribute('data-gradient');
        if (gradient) {
            icon.style.background = gradient;
        }
    });

    // Handle image fallback for static icons
    const staticIcons = document.querySelectorAll('.app-static-icon');
    staticIcons.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const fallbackIcon = this.nextElementSibling;
            if (fallbackIcon) {
                fallbackIcon.style.display = 'inline';
                fallbackIcon.style.color = 'white';
            }
            const gradient = this.getAttribute('data-fallback-gradient');
            if (gradient && this.parentElement) {
                this.parentElement.style.background = gradient;
            }
        });
    });
});

// App installation function
function installApp(appId) {
    // Show loading state
    const button = event.target.closest('button');
    const originalHtml = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Installation...';

    // Simulate app installation (replace with actual API call)
    setTimeout(() => {
        button.innerHTML = '<i class="bi bi-check-circle me-2"></i>Installé';
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-success');

        // Change to open button after a moment
        setTimeout(() => {
            button.innerHTML = '<i class="bi bi-arrow-right me-2"></i>Ouvrir';
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
            button.onclick = function () {
                window.location.href = getAppUrl(appId);
            };
        }, 1000);
    }, 2000);
}

// Get app URL based on ID
function getAppUrl(appId) {
    const appUrls = {
        'ai-assistant': '/language-ai/',
        'quiz': '/quiz/',
        'progress': '/progress/'
    };
    return appUrls[appId] || '#';
}