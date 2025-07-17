/**
 * Settings Core - Navigation and shared functionality
 * Simplified version focusing on navigation and coordination
 * 
 * This file provides:
 * - Navigation between settings tabs
 * - Auto-save functionality
 * - Search functionality
 * - Keyboard shortcuts
 * 
 * Utilities are available via window.settingsUtils:
 * - getCsrfToken()
 * - showTemporaryMessage(message, type)
 * - showFieldError/Success/Pending()
 * - validateField()
 * - handleFormSubmission()
 */

class SettingsManager {
    constructor() {
        this.currentTab = 'profile';
        this.autoSaveTimeout = null;
        this.searchTimeout = null;
        this.init();
    }

    init() {
        console.log('[Settings Core] Initializing settings navigation...');
        
        this.setupNavigation();
        this.setupSearch();
        this.setupAutoSave();
        this.setupKeyboardShortcuts();
        
        // Load saved tab from localStorage
        const savedTab = localStorage.getItem('settings-current-tab');
        if (savedTab) {
            this.switchTab(savedTab);
        }
        
        console.log('[Settings Core] Navigation initialized successfully');
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
        console.log(`[Settings Core] Switching to tab: ${tabId}`);
        
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
                console.log('[Settings Core] Auto-save successful:', result);
                
                // Handle profile picture update if present
                if (result.profile_picture_url && window.updateAllProfilePictures) {
                    window.updateAllProfilePictures(result.profile_picture_url);
                }
            } else {
                throw new Error('Save failed');
            }
        } catch (error) {
            console.error('[Settings Core] Auto-save error:', error);
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
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});

// Export for potential external use
window.SettingsManager = SettingsManager;