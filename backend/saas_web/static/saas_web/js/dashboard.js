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
    
    console.log('Applying Linguify gradients...');
    
    // Apply gradient only to app icons that don't have static images
    const appIcons = document.querySelectorAll('.app-icon-simple');
    appIcons.forEach(function(icon) {
        // Check if this icon has a static image (transparent background)
        const hasStaticIcon = icon.style.background === 'transparent' || 
                             icon.style.background.includes('transparent') ||
                             icon.querySelector('img');
        
        if (!hasStaticIcon) {
            // Only apply gradient if no static icon
            const customGradient = icon.getAttribute('data-gradient');
            if (!customGradient || customGradient.includes('#667eea')) {
                icon.style.background = 'linear-gradient(135deg, #2D5BBA 0%, #00D4AA 100%)';
                console.log('Applied Linguify gradient to icon without static image');
            }
        } else {
            console.log('Skipped icon with static image');
        }
    });
    
    // Force welcome banner gradient
    const welcomeBanner = document.querySelector('.welcome-banner');
    if (welcomeBanner) {
        welcomeBanner.style.background = 'linear-gradient(135deg, #2D5BBA 0%, #00D4AA 100%)';
        console.log('Applied Linguify gradient to welcome banner');
    }

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