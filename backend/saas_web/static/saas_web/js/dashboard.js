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

// Load and apply saved dashboard background
function loadDashboardBackground() {
    const savedBackground = localStorage.getItem('dashboard_background') || 'default';
    
    const backgroundColors = {
        // Couleurs neutres
        'default': '#f8fafc',
        'white': '#ffffff',
        'gray-light': '#f9fafb',
        'gray': '#f3f4f6',
        
        // Couleurs Linguify
        'linguify-light': 'linear-gradient(135deg, #f0f4ff 0%, #e0f2fe 100%)',
        'linguify-accent': 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
        'linguify-purple': 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
        
        // Couleurs premium
        'warm': 'linear-gradient(135deg, #fefbf3 0%, #fef7ed 100%)',
        'cool': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        'nature': 'linear-gradient(135deg, #f7fee7 0%, #ecfccb 100%)',
        
        // Mode sombre
        'dark': '#1f2937',
        'dark-blue': 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        
        // Compatibilité ancienne version
        'blue': '#eff6ff',
        'green': '#f0fdf4',
        'purple': '#faf5ff'
    };
    
    const color = backgroundColors[savedBackground] || backgroundColors['default'];
    document.body.style.setProperty('background', color, 'important');
    
    // Also apply to content area if it exists
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        contentArea.style.background = 'transparent';
    }
    
    // Remove all background classes first
    document.body.classList.remove(
        'bg-default', 'bg-white', 'bg-gray-light', 'bg-gray',
        'bg-linguify-light', 'bg-linguify-accent', 'bg-linguify-purple',
        'bg-warm', 'bg-cool', 'bg-nature', 
        'bg-dark', 'bg-dark-blue',
        'bg-blue', 'bg-green', 'bg-purple', // compatibility
        'dark-background' // old class
    );
    
    // Apply specific background class for automatic text color adaptation
    document.body.classList.add('bg-' + savedBackground);
    
    console.log('[Dashboard] Background applied:', savedBackground, color);
}

// Apply app icon gradients from data attributes
document.addEventListener('DOMContentLoaded', function () {
    // Initialize chat variables first
    initializeChatVariables();
    
    // Load dashboard background
    loadDashboardBackground();
    
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
    
    // Initialize drag & drop for app reordering
    console.log('DOM loaded, initializing drag & drop...');
    initializeDragAndDrop();
});

// Drag & Drop functionality for app reordering
function initializeDragAndDrop() {
    const appsContainer = document.querySelector('.apps-grid-container');
    if (!appsContainer) {
        console.log('Apps container not found');
        return;
    }
    
    const appLinks = appsContainer.querySelectorAll('.app-link');
    console.log(`Initializing drag & drop for ${appLinks.length} apps`);
    
    appLinks.forEach((appLink, index) => {
        const appCard = appLink.querySelector('.app-card-simple');
        if (!appCard) return;
        
        // Make the entire link draggable, not just the card
        appLink.draggable = true;
        appLink.setAttribute('data-app-index', index);
        appLink.setAttribute('data-app-name', appCard.querySelector('.app-name-simple')?.textContent?.trim() || '');
        
        // Add drag event listeners to the link
        appLink.addEventListener('dragstart', handleDragStart);
        appLink.addEventListener('dragend', handleDragEnd);
        
        // Add drop zone listeners
        appLink.addEventListener('dragover', handleDragOver);
        appLink.addEventListener('drop', handleDrop);
        appLink.addEventListener('dragenter', handleDragEnter);
        appLink.addEventListener('dragleave', handleDragLeave);
        
        // Add click handler with better drag detection
        appLink.addEventListener('click', handleAppLinkClick);
        
        // Add visual indicator that it's draggable
        appCard.style.cursor = 'grab';
        
        console.log(`Initialized drag for: ${appLink.getAttribute('data-app-name')}`);
    });
    
    console.log('Drag & drop initialization complete');
}

// Track drag state to prevent navigation
let isDragging = false;
let dragStartTime = 0;

function handleAppLinkClick(e) {
    // If we just finished dragging, prevent navigation
    const timeSinceDrag = Date.now() - dragStartTime;
    if (isDragging || timeSinceDrag < 300) {
        e.preventDefault();
        console.log('Click prevented due to recent drag operation');
        return false;
    }
    
    // Allow normal navigation
    const appName = this.getAttribute('data-app-name');
    console.log(`Navigating to app: ${appName} -> ${this.href}`);
}

let draggedElement = null;
let draggedIndex = null;

function handleDragStart(e) {
    draggedElement = this; // this is now the app-link
    draggedIndex = parseInt(this.getAttribute('data-app-index'));
    const appName = this.getAttribute('data-app-name');
    
    // Set drag state
    isDragging = true;
    dragStartTime = Date.now();
    
    console.log(`🚁 Drag started for: ${appName} at index ${draggedIndex}`);
    
    // Don't prevent default here - let the drag system work
    // e.preventDefault(); 
    
    // Add dragging class for visual feedback to the card inside
    const appCard = this.querySelector('.app-card-simple');
    if (appCard) {
        appCard.classList.add('dragging');
        appCard.style.cursor = 'grabbing';
    }
    
    // Set drag data - include app name for easier tracking
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', appName);
    e.dataTransfer.setData('application/app-index', draggedIndex.toString());
    
    console.log(`📦 Drag data set: ${appName}`);
}

function handleDragEnd(e) {
    console.log('🏁 Drag ended');
    
    // Reset visual state for the card inside
    const appCard = this.querySelector('.app-card-simple');
    if (appCard) {
        appCard.classList.remove('dragging');
        appCard.style.opacity = '';
        appCard.style.transform = '';
        appCard.style.cursor = 'grab';
    }
    
    // Reset drag state with a small delay to prevent immediate click
    setTimeout(() => {
        isDragging = false;
    }, 100);
    
    // Remove all drop zone highlights
    document.querySelectorAll('.app-link').forEach(link => {
        link.classList.remove('drag-over');
    });
    
    draggedElement = null;
    draggedIndex = null;
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    if (draggedElement && this !== draggedElement) {
        this.classList.add('drag-over');
        console.log(`📍 Enter drop zone: ${this.getAttribute('data-app-name')}`);
    }
}

function handleDragLeave(e) {
    // Only remove highlight if we're actually leaving the element
    if (!this.contains(e.relatedTarget)) {
        this.classList.remove('drag-over');
    }
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    this.classList.remove('drag-over');
    
    if (draggedElement && this !== draggedElement) {
        const targetIndex = Array.from(this.parentNode.children).indexOf(this);
        const draggedAppName = e.dataTransfer.getData('text/plain');
        const targetAppName = this.getAttribute('data-app-name');
        
        console.log(`🎯 Drop: "${draggedAppName}" -> "${targetAppName}" (${draggedIndex} -> ${targetIndex})`);
        
        // Perform the reorder
        reorderApps(draggedIndex, targetIndex);
    }
    
    return false;
}

function reorderApps(fromIndex, toIndex) {
    console.log(`🔄 Reordering: ${fromIndex} -> ${toIndex}`);
    
    const appsContainer = document.querySelector('.apps-grid-container');
    const appLinks = Array.from(appsContainer.children);
    
    // Extract app identifiers for backend update
    const appOrder = appLinks.map(link => {
        const appName = link.querySelector('.app-name-simple');
        return appName ? appName.textContent.trim() : '';
    });
    
    console.log('📋 Current order:', appOrder);
    
    // Move the element in the DOM
    const draggedLink = appLinks[fromIndex];
    const targetLink = appLinks[toIndex];
    
    if (fromIndex < toIndex) {
        // Moving forward
        targetLink.parentNode.insertBefore(draggedLink, targetLink.nextSibling);
    } else {
        // Moving backward
        targetLink.parentNode.insertBefore(draggedLink, targetLink);
    }
    
    // Update the app order array
    const movedApp = appOrder.splice(fromIndex, 1)[0];
    appOrder.splice(toIndex, 0, movedApp);
    
    console.log('📋 New order:', appOrder);
    
    // Re-initialize drag and drop with new indices
    setTimeout(() => {
        initializeDragAndDrop();
    }, 100);
    
    // Save the new order to backend
    saveAppOrder(appOrder);
    
    console.log('✅ Reorder complete');
}

function saveAppOrder(appOrder) {
    if (!window.csrfToken) {
        console.error('CSRF token not available');
        return;
    }
    
    fetch('/dashboard/save-app-order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({
            app_order: appOrder
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('App order saved successfully');
            // Optional: Show success notification
            showNotification('Ordre des applications sauvegardé', 'success');
        } else {
            console.error('Failed to save app order:', data.error);
            showNotification('Erreur lors de la sauvegarde', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving app order:', error);
        showNotification('Erreur de connexion', 'error');
    });
}

function showNotification(message, type = 'info') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => notification.style.opacity = '1', 100);
    
    // Fade out and remove
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

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