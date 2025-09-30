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
        console.log('[Settings Core] JavaScript navigation completely disabled for normal URL navigation');
        
        // Clear any saved tab state to prevent interference
        localStorage.removeItem('settings-current-tab');
        
        // Only setup non-interfering features
        this.setupNavigation(); // This only adds hover effects now
        this.setupSearch();
        this.setupAutoSave();
        this.setupKeyboardShortcuts();
        
        // DO NOT load saved tab or call switchTab() - let normal navigation work
        
        console.log('[Settings Core] Navigation initialized successfully');
    }

    setupNavigation() {
        console.log('[Settings Core] Setting up AJAX navigation...');

        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const targetUrl = item.getAttribute('href');

                // Ignorer les liens vides, invalides ou les ancres
                if (!targetUrl || targetUrl === '#' || targetUrl === '' || targetUrl.startsWith('javascript:')) {
                    console.log('[Settings Core] Ignoring invalid/empty link');
                    return;
                }

                e.preventDefault(); // Empêcher le rechargement de page

                console.log(`[Settings Core] Loading settings via AJAX: ${targetUrl}`);

                // Retirer la classe active de tous les items
                navItems.forEach(nav => nav.classList.remove('active'));
                // Ajouter la classe active à l'item cliqué
                item.classList.add('active');

                // Charger le contenu via AJAX
                this.loadSettingsContent(targetUrl);

                // Mettre à jour l'URL sans recharger
                window.history.pushState({}, '', targetUrl);
            });
        });

        // Gérer le bouton retour du navigateur
        window.addEventListener('popstate', () => {
            this.loadSettingsContent(window.location.pathname);
        });
    }

    async loadSettingsContent(url) {
        const mainContent = document.querySelector('.main-content-body');
        const headerContent = document.querySelector('.main-content-header');
        if (!mainContent) return;

        console.log(`[Settings Core] 🚀 Loading content via AJAX: ${url}`);
        const startTime = performance.now();

        try {
            // Afficher un loader avec animation
            mainContent.style.transition = 'opacity 0.15s ease';
            mainContent.style.opacity = '0.3';
            mainContent.style.pointerEvents = 'none';

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Failed to load content');

            const html = await response.text();

            // Parser le HTML pour extraire le contenu
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Mettre à jour le contenu principal
            const newContent = doc.querySelector('.main-content-body');
            if (newContent) {
                // IMPORTANT: Remplacer tout le innerHTML pour avoir le bon contenu
                mainContent.innerHTML = newContent.innerHTML;
                console.log('[Settings Core] 📝 Content updated from new page');
            } else {
                console.warn('[Settings Core] ⚠️ No .main-content-body found in response');
            }

            // Mettre à jour le header (titre, breadcrumb)
            const newHeader = doc.querySelector('.main-content-header');
            if (newHeader && headerContent) {
                headerContent.innerHTML = newHeader.innerHTML;
                console.log('[Settings Core] 📝 Header updated');
            }

            // Scroll vers le haut
            window.scrollTo({ top: 0, behavior: 'smooth' });

            // Réinitialiser les scripts pour le nouveau contenu
            this.reinitializeContentScripts();

            // Retirer le loader avec animation
            mainContent.style.opacity = '1';
            mainContent.style.pointerEvents = 'auto';

            const loadTime = (performance.now() - startTime).toFixed(2);
            console.log(`[Settings Core] ✅ Content loaded in ${loadTime}ms`);

        } catch (error) {
            console.error('[Settings Core] ❌ Error loading content:', error);
            // Fallback: recharger la page normalement
            console.log('[Settings Core] Falling back to normal navigation');
            window.location.href = url;
        }
    }

    reinitializeContentScripts() {
        // Réinitialiser les event listeners pour les formulaires
        this.setupAutoSave();

        // Déclencher un événement personnalisé pour que d'autres scripts puissent réagir
        document.dispatchEvent(new CustomEvent('settingsContentLoaded'));
    }

    switchTab(tabId) {
        console.log(`[Settings Core] switchTab() called with: ${tabId}`);
        // Cette méthode est maintenant gérée par loadSettingsContent
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
        // Skip auto-save if form doesn't have a valid action
        if (!form.action) {
            return;
        }

        // Liste des URLs à exclure de l'auto-save
        const excludedUrls = [
            'app-manager',
            'profile',      // Exclure la page profile qui a son propre système de sauvegarde
            'interface'     // Exclure interface aussi
        ];

        // Vérifier si l'URL contient une des patterns à exclure
        const shouldSkip = excludedUrls.some(pattern => form.action.includes(pattern));
        if (shouldSkip) {
            console.log('[Settings Core] Skipping auto-save for excluded page');
            return;
        }

        const indicator = this.showAutoSaveIndicator('Sauvegarde...');

        try {
            const formData = new FormData(form);

            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                             document.cookie.match(/csrftoken=([^;]+)/)?.[1];

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
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

// Initialize when DOM is ready (only once)
if (!window.settingsManagerInitialized) {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.settingsManager) {
            console.log('[Settings Core] Initializing SettingsManager...');
            window.settingsManager = new SettingsManager();
            window.settingsManagerInitialized = true;
        }
    });
}

// Export for potential external use
window.SettingsManager = SettingsManager;