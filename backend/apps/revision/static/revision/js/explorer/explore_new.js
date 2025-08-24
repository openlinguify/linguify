/**
 * Explore New JS - Fonctionnalités pour la page Explorer
 * Gestion du centre de notifications et des interactions UI
 */

// ===== NOTIFICATION CENTER =====
/**
 * Toggle du centre de notifications
 * Affiche/masque le panneau avec overlay
 */
function toggleNotificationCenter() {
    const center = document.getElementById('notificationCenter');
    const overlay = document.getElementById('notificationOverlay');
    const isVisible = center.style.display !== 'none';
    
    if (isVisible) {
        // Hide notification center
        center.style.display = 'none';
        overlay.classList.remove('show');
    } else {
        // Show notification center
        center.style.display = 'block';
        overlay.classList.add('show');
    }
}

/**
 * Filtrage des notifications par catégorie
 * Initialise les event listeners au chargement de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    const filters = document.querySelectorAll('.notification-filter');
    const items = document.querySelectorAll('.notification-item');
    
    filters.forEach(filter => {
        filter.addEventListener('click', function() {
            // Remove active class from all filters
            filters.forEach(f => f.classList.remove('active'));
            // Add active class to clicked filter
            this.classList.add('active');
            
            const filterType = this.getAttribute('data-filter');
            
            // Show/hide notifications based on filter
            items.forEach(item => {
                const itemType = item.getAttribute('data-type');
                if (filterType === 'all' || itemType === filterType) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});

// ===== NOTIFICATION ACTIONS =====
/**
 * Marquer toutes les notifications comme lues
 */
function markAllNotificationsRead() {
    console.log('🔔 Marking all notifications as read...');
    // TODO: Implémenter l'appel API
    window.notificationService?.success('Toutes les notifications ont été marquées comme lues');
}

/**
 * Ouvrir les paramètres de notifications
 */
function showNotificationSettings() {
    console.log('⚙️ Opening notification settings...');
    // TODO: Ouvrir le modal des paramètres de notifications
    const modal = document.getElementById('notificationSettingsModal');
    if (modal) {
        // Utiliser Bootstrap modal si disponible
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = new window.bootstrap.Modal(modal);
            modalInstance.show();
        } else {
            // Fallback pour Tailwind modals
            modal.style.display = 'block';
            modal.setAttribute('aria-hidden', 'false');
        }
    }
}

/**
 * Ouvrir toutes les notifications dans un modal
 */
function showAllNotifications() {
    console.log('📋 Opening all notifications modal...');
    // TODO: Ouvrir le modal complet des notifications
    const modal = document.getElementById('allNotificationsModal');
    if (modal) {
        // Utiliser Bootstrap modal si disponible
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = new window.bootstrap.Modal(modal);
            modalInstance.show();
        } else {
            // Fallback pour Tailwind modals
            modal.style.display = 'block';
            modal.setAttribute('aria-hidden', 'false');
        }
    }
}

/**
 * Sauvegarder les paramètres de notifications
 */
function saveNotificationSettings() {
    console.log('💾 Saving notification settings...');
    
    // Récupérer les valeurs des paramètres
    const settings = {
        enableNotifications: document.getElementById('enableNotifications')?.checked || false,
        enableSoundNotifications: document.getElementById('enableSoundNotifications')?.checked || false,
        enableBadgeNotifications: document.getElementById('enableBadgeNotifications')?.checked || false,
        notifyNewDecks: document.getElementById('notifyNewDecks')?.checked || false,
        notifyFavoritesUpdates: document.getElementById('notifyFavoritesUpdates')?.checked || false,
        notifyCollectionsActivity: document.getElementById('notifyCollectionsActivity')?.checked || false,
        notifyRecommendations: document.getElementById('notifyRecommendations')?.checked || false,
        notifySystem: document.getElementById('notifySystem')?.checked || false,
        notificationFrequency: document.getElementById('notificationFrequency')?.value || 'daily'
    };
    
    // TODO: Envoyer les paramètres au serveur via API
    console.log('Settings to save:', settings);
    
    // Fermer le modal
    const modal = document.getElementById('notificationSettingsModal');
    if (modal) {
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = window.bootstrap.Modal.getInstance(modal);
            if (modalInstance) modalInstance.hide();
        } else {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
    }
    
    // Afficher un message de succès
    if (window.notificationService) {
        window.notificationService.success('Paramètres de notifications sauvegardés');
    } else {
        console.log('✅ Notification settings saved successfully');
    }
}

// ===== SIDEBAR MANAGEMENT =====
/**
 * Toggle de la sidebar pour les filtres
 */
function toggleSidebar() {
    const sidebar = document.getElementById('exploreSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar) {
        const isVisible = sidebar.classList.contains('show');
        
        if (isVisible) {
            sidebar.classList.remove('show');
            if (overlay) overlay.style.display = 'none';
        } else {
            sidebar.classList.add('show');
            if (overlay) overlay.style.display = 'block';
        }
    }
}

// ===== NOTIFICATION HANDLERS =====
/**
 * Gestionnaires pour les actions de notification individuelles
 */
document.addEventListener('DOMContentLoaded', function() {
    // Event listeners pour les boutons principaux
    const notificationBtn = document.getElementById('notificationBtn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', toggleNotificationCenter);
    }
    
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    const notificationOverlay = document.getElementById('notificationOverlay');
    if (notificationOverlay) {
        notificationOverlay.addEventListener('click', toggleNotificationCenter);
    }
    
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }
    
    // Event listeners pour les actions de notification
    document.addEventListener('click', function(e) {
        // Boutons d'action des notifications
        if (e.target.classList.contains('notification-action-btn')) {
            const action = e.target.textContent.trim().toLowerCase();
            const notificationItem = e.target.closest('.notification-item');
            const title = notificationItem.querySelector('.notification-title').textContent;
            
            if (action === 'voir') {
                console.log(`👀 Viewing notification: ${title}`);
                // TODO: Naviguer vers le contenu de la notification
            } else if (action === 'ignorer') {
                console.log(`🚫 Ignoring notification: ${title}`);
                // Supprimer visuellement la notification
                notificationItem.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => {
                    notificationItem.remove();
                    // TODO: Mettre à jour les compteurs
                }, 300);
            }
        }
        
        // Gestionnaires pour les boutons avec IDs spécifiques
        if (e.target.id === 'saveNotificationSettingsBtn') {
            saveNotificationSettings();
            e.preventDefault();
        } else if (e.target.id === 'markAllNotificationsReadBtn') {
            markAllNotificationsRead();
            e.preventDefault();
        }
        
        // Gestionnaires pour les actions de notification management par contenu
        const text = e.target.textContent?.trim();
        if (text) {
            if (text.includes('Marquer tout comme lu')) {
                markAllNotificationsRead();
                e.preventDefault();
            } else if (text.includes('Paramètres') && e.target.title === 'Paramètres') {
                showNotificationSettings();
                e.preventDefault();
            } else if (text.includes('Voir toutes les notifications')) {
                showAllNotifications();
                e.preventDefault();
            }
        }
    });
});

// ===== ANIMATION UTILITIES =====
/**
 * Animation de sortie pour les notifications supprimées
 */
const slideOutAnimation = `
@keyframes slideOutRight {
    from {
        opacity: 1;
        transform: translateX(0);
    }
    to {
        opacity: 0;
        transform: translateX(100%);
    }
}
`;

// Injecter l'animation dans le document
if (!document.getElementById('explore-animations')) {
    const style = document.createElement('style');
    style.id = 'explore-animations';
    style.textContent = slideOutAnimation;
    document.head.appendChild(style);
}

// ===== FILTER FUNCTIONS =====
/**
 * Select status filter for Explorer page
 * @param {string} value - Filter value
 * @param {string} text - Display text
 */
function selectStatusFilter(value, text) {
    try {
        console.log(`📊 Explorer status filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('statusFilterText');
        const items = document.querySelectorAll('#statusFilterDropdown .dropdown-item');
        
        if (!textElement) {
            console.warn('⚠️ Status filter text element not found in Explorer');
            return;
        }
        
        textElement.textContent = text;
        
        // Update selected state
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('⚠️ Error updating item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Trigger search update if main explorer module is available
        if (window.explorerMain && typeof window.explorerMain.performSearch === 'function') {
            window.explorerMain.performSearch();
        } else {
            console.log('🔍 Explorer main module not available, filter stored for next search');
        }
        
        console.log('✅ Explorer status filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in Explorer selectStatusFilter:', error.message);
    }
}

/**
 * Select sort filter for Explorer page
 * @param {string} value - Sort value
 * @param {string} text - Display text
 */
function selectSortFilter(value, text) {
    try {
        console.log(`📊 Explorer sort filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('sortFilterText');
        const items = document.querySelectorAll('#sortFilterDropdown .dropdown-item');
        
        if (!textElement) {
            console.warn('⚠️ Sort filter text element not found in Explorer');
            return;
        }
        
        textElement.textContent = text;
        
        // Update selected state
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('⚠️ Error updating sort item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Trigger search update if main explorer module is available
        if (window.explorerMain && typeof window.explorerMain.performSearch === 'function') {
            window.explorerMain.performSearch();
        } else {
            console.log('🔍 Explorer main module not available, filter stored for next search');
        }
        
        console.log('✅ Explorer sort filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in Explorer selectSortFilter:', error.message);
    }
}

/**
 * Select tags filter for Explorer page
 * @param {string} value - Tag value
 * @param {string} text - Display text
 */
function selectTagsFilter(value, text) {
    try {
        console.log(`📊 Explorer tags filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('tagsFilterText');
        const items = document.querySelectorAll('#tagsFilterDropdown .dropdown-item');
        
        if (!textElement) {
            console.warn('⚠️ Tags filter text element not found in Explorer');
            return;
        }
        
        textElement.textContent = text;
        
        // Update selected state
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('⚠️ Error updating tags item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Trigger search update if main explorer module is available
        if (window.explorerMain && typeof window.explorerMain.performSearch === 'function') {
            window.explorerMain.performSearch();
        } else {
            console.log('🔍 Explorer main module not available, filter stored for next search');
        }
        
        console.log('✅ Explorer tags filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in Explorer selectTagsFilter:', error.message);
    }
}

// ===== EXPORTS POUR AUTRES MODULES =====
window.exploreNewModule = {
    toggleNotificationCenter,
    markAllNotificationsRead,
    showNotificationSettings,
    showAllNotifications,
    toggleSidebar,
    selectStatusFilter,
    selectSortFilter,
    selectTagsFilter
};

// Make filter functions globally available for navbar onclick handlers
window.selectStatusFilter = selectStatusFilter;
window.selectSortFilter = selectSortFilter;
window.selectTagsFilter = selectTagsFilter;

console.log('🚀 Explore New JS module loaded successfully');