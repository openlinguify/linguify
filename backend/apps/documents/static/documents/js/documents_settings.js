/**
 * Documents Settings Management
 * Handles saving, loading, and resetting documents settings
 */

const documentsSettings = {
    // API endpoints
    endpoints: {
        save: '/documents/api/v1/save-settings/',
        get: '/documents/api/v1/get-settings/',
        reset: '/documents/api/v1/reset-settings/'
    },

    // Initialize settings on page load
    init: function() {
        this.loadSettings();
        console.log('Documents settings initialized');
    },

    // Get CSRF token for Django
    getCsrfToken: function() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            return token.value;
        }
        // Fallback to cookie method
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    },

    // Collect all settings from the form
    collectSettings: function() {
        const form = document.getElementById('documents-settings-form');
        if (!form) {
            console.error('Documents settings form not found');
            return null;
        }

        const settings = {
            defaultContentType: document.getElementById('default-content-type')?.value || 'markdown',
            defaultVisibility: document.getElementById('default-visibility')?.value || 'private',
            autoSave: document.getElementById('auto-save')?.checked || false,
            editorTheme: document.getElementById('editor-theme')?.value || 'light',
            fontSize: document.getElementById('font-size')?.value || '14',
            livePreview: document.getElementById('live-preview')?.checked || false,
            commentNotifications: document.getElementById('comment-notifications')?.checked || false,
            shareNotifications: document.getElementById('share-notifications')?.checked || false,
            defaultPermissions: document.getElementById('default-permissions')?.value || 'edit',
            showCursors: document.getElementById('show-cursors')?.checked || false
        };

        return settings;
    },

    // Apply settings to the form
    applySettings: function(settings) {
        if (!settings) return;

        // Set select values
        const selects = [
            { id: 'default-content-type', key: 'defaultContentType', default: 'markdown' },
            { id: 'default-visibility', key: 'defaultVisibility', default: 'private' },
            { id: 'editor-theme', key: 'editorTheme', default: 'light' },
            { id: 'font-size', key: 'fontSize', default: '14' },
            { id: 'default-permissions', key: 'defaultPermissions', default: 'edit' }
        ];

        selects.forEach(({ id, key, default: defaultValue }) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = settings[key] || defaultValue;
            }
        });

        // Set checkbox values
        const checkboxes = [
            { id: 'auto-save', key: 'autoSave', default: true },
            { id: 'live-preview', key: 'livePreview', default: true },
            { id: 'comment-notifications', key: 'commentNotifications', default: true },
            { id: 'share-notifications', key: 'shareNotifications', default: true },
            { id: 'show-cursors', key: 'showCursors', default: true }
        ];

        checkboxes.forEach(({ id, key, default: defaultValue }) => {
            const element = document.getElementById(id);
            if (element) {
                element.checked = settings[key] !== undefined ? settings[key] : defaultValue;
            }
        });
    },

    // Save settings to backend
    save: function() {
        const settings = this.collectSettings();
        if (!settings) {
            this.showNotification('Erreur lors de la collecte des paramètres', 'error');
            return;
        }

        // Show loading state
        const saveBtn = document.querySelector('[onclick="documentsSettings.save()"]');
        if (saveBtn) {
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Sauvegarde...';
            saveBtn.disabled = true;

            // Restore button after save attempt
            setTimeout(() => {
                saveBtn.innerHTML = originalText;
                saveBtn.disabled = false;
            }, 2000);
        }

        // Send to backend
        fetch(this.endpoints.save, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Paramètres sauvegardés avec succès!', 'success');
                // Also save to localStorage as backup
                localStorage.setItem('documentsSettings', JSON.stringify(settings));
            } else {
                throw new Error(data.message || 'Erreur lors de la sauvegarde');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            // Fallback to localStorage
            localStorage.setItem('documentsSettings', JSON.stringify(settings));
            this.showNotification('Paramètres sauvegardés localement', 'warning');
        });
    },

    // Load settings from backend
    loadSettings: function() {
        fetch(this.endpoints.get, {
            method: 'GET',
            headers: {
                'X-CSRFToken': this.getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.applySettings(data.settings);
            } else {
                throw new Error('Failed to load settings from backend');
            }
        })
        .catch(error => {
            console.error('Load error:', error);
            // Fallback to localStorage
            const localSettings = localStorage.getItem('documentsSettings');
            if (localSettings) {
                try {
                    const settings = JSON.parse(localSettings);
                    this.applySettings(settings);
                    console.log('Loaded settings from localStorage');
                } catch (e) {
                    console.error('Failed to parse local settings:', e);
                }
            }
        });
    },

    // Reset settings to defaults
    reset: function() {
        if (!confirm('Êtes-vous sûr de vouloir réinitialiser tous les paramètres aux valeurs par défaut ?')) {
            return;
        }

        // Show loading state
        const resetBtn = document.querySelector('[onclick="documentsSettings.reset()"]');
        if (resetBtn) {
            const originalText = resetBtn.innerHTML;
            resetBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Réinitialisation...';
            resetBtn.disabled = true;

            setTimeout(() => {
                resetBtn.innerHTML = originalText;
                resetBtn.disabled = false;
            }, 2000);
        }

        // Reset on backend
        fetch(this.endpoints.reset, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Apply default settings
                this.applyDefaults();
                this.showNotification('Paramètres réinitialisés', 'info');
                // Remove from localStorage
                localStorage.removeItem('documentsSettings');
            } else {
                throw new Error(data.message || 'Erreur lors de la réinitialisation');
            }
        })
        .catch(error => {
            console.error('Reset error:', error);
            // Fallback reset
            this.applyDefaults();
            localStorage.removeItem('documentsSettings');
            this.showNotification('Paramètres réinitialisés localement', 'warning');
        });
    },

    // Apply default settings
    applyDefaults: function() {
        const defaults = {
            defaultContentType: 'markdown',
            defaultVisibility: 'private',
            autoSave: true,
            editorTheme: 'light',
            fontSize: '14',
            livePreview: true,
            commentNotifications: true,
            shareNotifications: true,
            defaultPermissions: 'edit',
            showCursors: true
        };

        this.applySettings(defaults);
    },

    // Show notification to user
    showNotification: function(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.settings-notification');
        existingNotifications.forEach(notification => notification.remove());

        // Create new notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} settings-notification position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 400px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 8px;
            border: none;
        `;

        // Set icon based on type
        let icon = 'bi-info-circle';
        if (type === 'success') icon = 'bi-check-circle';
        else if (type === 'error' || type === 'danger') icon = 'bi-x-circle';
        else if (type === 'warning') icon = 'bi-exclamation-triangle';

        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi ${icon} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 4000);
    },

    // Export current settings as JSON
    exportSettings: function() {
        const settings = this.collectSettings();
        if (!settings) return;

        const dataStr = JSON.stringify(settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'documents-settings.json';
        link.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Paramètres exportés', 'success');
    },

    // Import settings from JSON file
    importSettings: function(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const settings = JSON.parse(e.target.result);
                this.applySettings(settings);
                this.showNotification('Paramètres importés avec succès', 'success');
            } catch (error) {
                this.showNotification('Erreur lors de l\'import des paramètres', 'error');
                console.error('Import error:', error);
            }
        };
        reader.readAsText(file);
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    documentsSettings.init();
});

// Global functions for button onclick handlers
function saveDocumentsSettings() {
    documentsSettings.save();
}

function resetDocumentsSettings() {
    documentsSettings.reset();
}

function exportDocumentsSettings() {
    documentsSettings.exportSettings();
}

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = documentsSettings;
}