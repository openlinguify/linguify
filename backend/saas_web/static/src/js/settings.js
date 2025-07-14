/**
 * Settings Page Improvements - v2024.07.14
 * Enhanced UX with auto-save, search, and better navigation
 */

class SettingsManager {
    constructor() {
        this.currentTab = 'profile';
        this.autoSaveTimeout = null;
        this.searchTimeout = null;
        this.init();
    }

    init() {
        console.log('[Settings] Initializing improved settings manager...');
        
        this.setupNavigation();
        this.setupSearch();
        this.setupAutoSave();
        this.setupThemePreview();
        this.setupSectionCollapse();
        this.setupFormValidation();
        this.setupKeyboardShortcuts();
        
        // Load saved tab from localStorage
        const savedTab = localStorage.getItem('settings-current-tab');
        if (savedTab) {
            this.switchTab(savedTab);
        }
        
        console.log('[Settings] Settings manager initialized successfully');
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const tabId = item.getAttribute('data-tab');
                if (tabId) {
                    this.switchTab(tabId);
                }
            });
        });
    }

    switchTab(tabId) {
        console.log(`[Settings] Switching to tab: ${tabId}`);
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[data-tab="${tabId}"]`);
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        const activeContent = document.getElementById(tabId);
        if (activeContent) {
            activeContent.classList.add('active');
        }
        
        // Update page title
        this.updatePageTitle(tabId);
        
        // Save current tab
        this.currentTab = tabId;
        localStorage.setItem('settings-current-tab', tabId);
        
        // Update URL without page reload
        const newUrl = `${window.location.pathname}?tab=${tabId}`;
        window.history.replaceState({}, '', newUrl);
    }

    updatePageTitle(tabId) {
        const titleElement = document.querySelector('.page-title');
        const subtitleElement = document.querySelector('.page-subtitle');
        
        const titles = {
            'profile': {
                title: 'Profil & Compte',
                subtitle: 'Gérez vos informations personnelles et paramètres de compte'
            },
            'learning': {
                title: 'Apprentissage',
                subtitle: 'Configurez vos objectifs et préférences d\'apprentissage'
            },
            'interface': {
                title: 'Interface & Expérience',
                subtitle: 'Personnalisez l\'apparence et l\'accessibilité'
            },
            'voice': {
                title: 'Assistant Vocal',
                subtitle: 'Paramètres de reconnaissance et synthèse vocale'
            },
            'chat': {
                title: 'Chat',
                subtitle: 'Paramètres de messagerie et notifications'
            },
            'community': {
                title: 'Communauté',
                subtitle: 'Paramètres sociaux et interactions communautaires'
            },
            'notes': {
                title: 'Notes',
                subtitle: 'Paramètres de prise de notes et organisation'
            },
            'quiz': {
                title: 'Quiz',
                subtitle: 'Paramètres des quiz et suivi des performances'
            }
        };
        
        const tabInfo = titles[tabId] || { title: 'Paramètres', subtitle: '' };
        
        if (titleElement) {
            titleElement.textContent = tabInfo.title;
        }
        if (subtitleElement) {
            subtitleElement.textContent = tabInfo.subtitle;
        }
    }

    setupSearch() {
        const searchInput = document.querySelector('.search-input');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value.toLowerCase());
            }, 300);
        });
    }

    performSearch(query) {
        const navItems = document.querySelectorAll('.nav-item');
        const sections = document.querySelectorAll('.content-section');
        
        if (!query) {
            // Reset visibility
            navItems.forEach(item => item.style.display = 'flex');
            sections.forEach(section => section.style.display = 'block');
            return;
        }
        
        // Search in navigation
        navItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(query) ? 'flex' : 'none';
        });
        
        // Search in content sections
        sections.forEach(section => {
            const text = section.textContent.toLowerCase();
            section.style.display = text.includes(query) ? 'block' : 'none';
        });
    }

    setupAutoSave() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    this.scheduleAutoSave(form);
                });
                
                input.addEventListener('change', () => {
                    this.scheduleAutoSave(form);
                });
            });
        });
    }

    scheduleAutoSave(form) {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.autoSave(form);
        }, 1000);
    }

    async autoSave(form) {
        const indicator = this.showAutoSaveIndicator('Sauvegarde...');
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.updateAutoSaveIndicator(indicator, 'Sauvegardé', 'success');
                console.log('[Settings] Auto-save successful:', result);
            } else {
                throw new Error('Save failed');
            }
        } catch (error) {
            console.error('[Settings] Auto-save error:', error);
            this.updateAutoSaveIndicator(indicator, 'Erreur de sauvegarde', 'error');
        }
    }

    showAutoSaveIndicator(message) {
        let indicator = document.querySelector('.auto-save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'auto-save-indicator';
            document.body.appendChild(indicator);
        }
        
        indicator.textContent = message;
        indicator.classList.remove('error');
        indicator.classList.add('show');
        
        return indicator;
    }

    updateAutoSaveIndicator(indicator, message, type) {
        indicator.textContent = message;
        if (type === 'error') {
            indicator.classList.add('error');
        }
        
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }

    setupThemePreview() {
        const themeOptions = document.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.getAttribute('data-theme');
                this.previewTheme(theme);
                
                // Update selection
                themeOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
            });
        });
        
        const colorOptions = document.querySelectorAll('.color-option');
        colorOptions.forEach(option => {
            option.addEventListener('click', () => {
                const color = option.getAttribute('data-color');
                this.previewColor(color);
                
                // Update selection
                colorOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
            });
        });
    }

    previewTheme(theme) {
        const body = document.body;
        body.classList.remove('theme-light', 'theme-dark', 'theme-auto');
        
        if (theme === 'dark') {
            body.classList.add('theme-dark');
        } else if (theme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
        } else {
            body.classList.add('theme-light');
        }
    }

    previewColor(color) {
        const root = document.documentElement;
        const colors = {
            violet: '#8b5cf6',
            blue: '#3b82f6',
            green: '#10b981',
            red: '#ef4444',
            orange: '#f59e0b'
        };
        
        if (colors[color]) {
            root.style.setProperty('--accent-color', colors[color]);
        }
    }

    setupSectionCollapse() {
        const sectionToggles = document.querySelectorAll('.section-toggle');
        sectionToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const section = toggle.closest('.content-section');
                const content = section.querySelector('.section-content');
                
                if (content.classList.contains('collapsed')) {
                    content.classList.remove('collapsed');
                    toggle.innerHTML = '<i class="bi bi-chevron-up"></i>';
                } else {
                    content.classList.add('collapsed');
                    toggle.innerHTML = '<i class="bi bi-chevron-down"></i>';
                }
            });
        });
    }

    setupFormValidation() {
        const inputs = document.querySelectorAll('input[required], input[type="email"], input[type="tel"]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });
    }

    validateField(input) {
        const value = input.value.trim();
        let isValid = true;
        let message = '';
        
        // Required field validation
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            message = 'Ce champ est requis';
        }
        
        // Email validation
        if (input.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Format d\'email invalide';
            }
        }
        
        // Phone validation
        if (input.type === 'tel' && value) {
            const phoneRegex = /^\+\d{1,3}\d{8,14}$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                message = 'Format de téléphone invalide';
            }
        }
        
        // Update field appearance
        input.classList.remove('is-valid', 'is-invalid');
        input.classList.add(isValid ? 'is-valid' : 'is-invalid');
        
        // Update feedback message
        let feedback = input.parentNode.querySelector('.form-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'form-feedback';
            input.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.className = `form-feedback ${isValid ? 'form-success' : 'form-error'}`;
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const activeForm = document.querySelector('.tab-content.active form');
                if (activeForm) {
                    this.autoSave(activeForm);
                }
            }
            
            // Ctrl/Cmd + F to search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Numbers 1-8 to switch tabs
            if (e.ctrlKey && e.key >= '1' && e.key <= '8') {
                e.preventDefault();
                const tabs = ['profile', 'interface', 'voice', 'learning', 'chat', 'community', 'notes', 'quiz'];
                const tabIndex = parseInt(e.key) - 1;
                if (tabs[tabIndex]) {
                    this.switchTab(tabs[tabIndex]);
                }
            }
        });
    }

    // Public API methods
    getSetting(key) {
        return localStorage.getItem(`settings-${key}`);
    }

    setSetting(key, value) {
        localStorage.setItem(`settings-${key}`, value);
    }

    resetSettings() {
        if (confirm('Êtes-vous sûr de vouloir réinitialiser tous les paramètres ?')) {
            // Clear localStorage
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('settings-')) {
                    localStorage.removeItem(key);
                }
            });
            
            // Reload page
            window.location.reload();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});

// Export for potential external use
window.SettingsManager = SettingsManager;

// Additional functions from original settings.js that are critical
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.cookie.match(/csrftoken=([^;]+)/)?.[1];
}

function showTemporaryMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Profile picture handling
function validateProfilePicture(event) {
    const input = event.target;
    const file = input.files[0];
    const feedback = getOrCreateFeedback(input, 'picture-feedback');
    
    if (!file) {
        feedback.textContent = '';
        input.classList.remove('is-invalid', 'is-valid');
        resetProfilePicturePreview();
        return;
    }
    
    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showFieldError(input, feedback, 'Format non supporté. Utilisez JPG, PNG ou WEBP');
        resetProfilePicturePreview();
        return;
    }
    
    // Check file size (5MB max)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        showFieldError(input, feedback, 'Fichier trop volumineux. Maximum 5MB');
        resetProfilePicturePreview();
        return;
    }
    
    showFieldSuccess(input, feedback, `Image valide (${(file.size / 1024 / 1024).toFixed(1)}MB)`);
    previewProfilePicture(file);
}

function previewProfilePicture(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const avatars = document.querySelectorAll('.user-avatar img');
        avatars.forEach(avatar => {
            avatar.src = e.target.result;
        });
    };
    reader.readAsDataURL(file);
}

function resetProfilePicturePreview() {
    const avatars = document.querySelectorAll('.user-avatar img');
    avatars.forEach(avatar => {
        const originalSrc = avatar.getAttribute('data-original-src');
        if (originalSrc) {
            avatar.src = originalSrc;
        }
    });
}

function updateAllProfilePictures(newUrl) {
    const avatars = document.querySelectorAll('.user-avatar img');
    avatars.forEach(avatar => {
        avatar.src = newUrl;
        avatar.setAttribute('data-original-src', newUrl);
    });
}

// Form validation utilities
function getOrCreateFeedback(input, id) {
    let feedback = document.getElementById(id);
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.id = id;
        feedback.className = 'form-feedback';
        feedback.style.fontSize = '12px';
        feedback.style.marginTop = '4px';
        input.parentNode.appendChild(feedback);
    }
    return feedback;
}

function showFieldError(input, feedback, message) {
    input.classList.remove('is-valid', 'is-pending');
    input.classList.add('is-invalid');
    feedback.textContent = message;
    feedback.style.color = '#dc3545';
}

function showFieldSuccess(input, feedback, message) {
    input.classList.remove('is-invalid', 'is-pending');
    input.classList.add('is-valid');
    feedback.textContent = message;
    feedback.style.color = '#198754';
}

function showFieldPending(input, feedback, message) {
    input.classList.remove('is-invalid', 'is-valid');
    input.classList.add('is-pending');
    feedback.textContent = message;
    feedback.style.color = '#6c757d';
}

// Account management functions
async function suspendAccount() {
    if (confirm('Êtes-vous sûr de vouloir suspendre temporairement votre compte ? Vous pourrez le réactiver à tout moment.')) {
        try {
            showTemporaryMessage('Suspension du compte en cours...', 'info');
            
            const response = await fetch('/auth/api/suspend-account/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showTemporaryMessage('Compte suspendu avec succès. Vous allez être déconnecté.', 'success');
                setTimeout(() => {
                    window.location.href = '/auth/logout/';
                }, 2000);
            } else {
                showTemporaryMessage('Erreur lors de la suspension: ' + (result.error || 'Erreur inconnue'), 'error');
            }
        } catch (error) {
            console.error('Suspension error:', error);
            showTemporaryMessage('Erreur de connexion lors de la suspension', 'error');
        }
    }
}

async function exportData() {
    if (confirm('Souhaitez-vous exporter toutes vos données personnelles ?')) {
        try {
            showTemporaryMessage('Export des données en cours...', 'info');
            
            const response = await fetch('/auth/api/export-data/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showTemporaryMessage('Export demandé avec succès ! Vous recevrez un email avec vos données dans quelques minutes.', 'success');
                
                if (result.download_url) {
                    const link = document.createElement('a');
                    link.href = result.download_url;
                    link.download = `linguify_data_export_${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            } else {
                showTemporaryMessage('Erreur lors de l\'export: ' + (result.error || 'Erreur inconnue'), 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            showTemporaryMessage('Erreur de connexion lors de l\'export', 'error');
        }
    }
}

async function deleteAccount() {
    const confirmText = 'SUPPRIMER';
    const userInput = prompt(
        `⚠️ ATTENTION : Cette action est irréversible !\n\n` +
        `Toutes vos données seront définitivement supprimées :\n` +
        `• Profil utilisateur\n` +
        `• Progression d'apprentissage\n` +
        `• Notes et flashcards\n` +
        `• Historique d'activité\n\n` +
        `Pour confirmer, tapez exactement : ${confirmText}`
    );
    
    if (userInput === confirmText) {
        if (confirm('Dernière confirmation : êtes-vous absolument certain de vouloir supprimer votre compte ?')) {
            try {
                showTemporaryMessage('Suppression du compte en cours...', 'warning');
                
                const response = await fetch('/auth/api/delete-account/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        confirmation: confirmText,
                        immediate: false
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(
                        `Votre compte a été programmé pour suppression.\n\n` +
                        `• Date de suppression : ${new Date(result.deletion_date).toLocaleDateString('fr-FR')}\n` +
                        `• Vous avez ${result.days_remaining} jours pour annuler\n` +
                        `• Un email de confirmation vous a été envoyé\n\n` +
                        `Vous pouvez annuler cette suppression en vous reconnectant avant la date limite.`
                    );
                    
                    setTimeout(() => {
                        window.location.href = '/auth/logout/';
                    }, 3000);
                } else {
                    showTemporaryMessage('Erreur lors de la suppression: ' + (result.error || 'Erreur inconnue'), 'error');
                }
            } catch (error) {
                console.error('Account deletion error:', error);
                showTemporaryMessage('Erreur de connexion lors de la suppression', 'error');
            }
        }
    } else if (userInput !== null) {
        alert('Texte de confirmation incorrect. Suppression annulée.');
    }
}

// Voice testing functions
function testVoice() {
    const utterance = new SpeechSynthesisUtterance('Test de l\'assistant vocal Linguify. Votre configuration fonctionne correctement !');
    
    const voiceSpeed = document.querySelector('select[name="speech_rate"]')?.value || 'normal';
    const voicePitch = document.querySelector('input[name="voice_pitch"]')?.value || 1;
    
    switch (voiceSpeed) {
        case 'slow':
            utterance.rate = 0.7;
            break;
        case 'fast':
            utterance.rate = 1.3;
            break;
        default:
            utterance.rate = 1.0;
    }
    
    utterance.pitch = voicePitch;
    utterance.lang = 'fr-FR';
    
    speechSynthesis.speak(utterance);
}

function testMicrophone() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Votre navigateur ne supporte pas l\'accès au microphone.');
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            alert('Microphone détecté et fonctionnel ! 🎤');
            stream.getTracks().forEach(track => track.stop());
        })
        .catch(error => {
            console.error('Erreur microphone:', error);
            alert('Impossible d\'accéder au microphone. Vérifiez les permissions de votre navigateur.');
        });
}

// Form submission handling
async function handleFormSubmission(form) {
    try {
        showTemporaryMessage('Sauvegarde en cours...', 'info');
        
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showTemporaryMessage(result.message, 'success');
            
            // Update profile picture if a new one was uploaded
            if (result.profile_picture_url) {
                updateAllProfilePictures(result.profile_picture_url);
            }
        } else {
            showTemporaryMessage(result.message || 'Erreur lors de la sauvegarde', 'error');
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showTemporaryMessage('Erreur de connexion', 'error');
    }
}

// Enhanced initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the main settings manager
    window.settingsManager = new SettingsManager();
    
    // Setup profile picture validation
    const profilePictureInput = document.querySelector('input[name="profile_picture"]');
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', validateProfilePicture);
    }
    
    // Setup voice testing buttons
    const testVoiceBtn = document.querySelector('button[onclick*="testVoice"]');
    if (testVoiceBtn) {
        testVoiceBtn.addEventListener('click', testVoice);
    }
    
    const testMicBtn = document.querySelector('button[onclick*="testMicrophone"]');
    if (testMicBtn) {
        testMicBtn.addEventListener('click', testMicrophone);
    }
    
    // Setup form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmission(form);
        });
    });
    
    console.log('[Settings] Enhanced settings manager initialized with all features');
});

// Make critical functions globally available
window.suspendAccount = suspendAccount;
window.exportData = exportData;
window.deleteAccount = deleteAccount;
window.testVoice = testVoice;
window.testMicrophone = testMicrophone;