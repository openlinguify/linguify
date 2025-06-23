/**
 * Language Selector - Refactored Version
 * Simplified and working implementation
 */

class LanguageSelector {
    constructor() {
        this.currentLanguage = 'fr';
        this.dropdownOpen = false;
        this.availableLanguages = {
            'fr': { name: 'Français', flag: 'fr.png', progress: 25, units: 120 },
            'en': { name: 'English', flag: 'gb.png', progress: 0, units: 95 },
            'es': { name: 'Español', flag: 'es.png', progress: 0, units: 88 },
            'de': { name: 'Deutsch', flag: 'de.png', progress: 0, units: 92 },
            'it': { name: 'Italiano', flag: 'it.png', progress: 0, units: 85 }
        };
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
        
        this.loadUserLanguagePreference();
    }
    
    setupEventListeners() {
        console.log('🔧 Setting up language selector...');
        
        // Single event listener for all clicks
        document.addEventListener('click', (e) => this.handleDocumentClick(e));
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.dropdownOpen) {
                this.closeDropdown();
            }
        });
    }
    
    handleDocumentClick(e) {
        const button = e.target.closest('.current-language-btn');
        const option = e.target.closest('.language-option');
        const dropdown = e.target.closest('.language-dropdown');
        
        // Handle button click
        if (button) {
            e.preventDefault();
            e.stopPropagation();
            this.toggleDropdown();
            return;
        }
        
        // Handle language option click
        if (option) {
            e.preventDefault();
            e.stopPropagation();
            const langCode = option.dataset.lang;
            this.selectLanguage(langCode);
            return;
        }
        
        // Click outside to close (not on dropdown or button)
        if (this.dropdownOpen && !dropdown) {
            this.closeDropdown();
        }
    }
    
    toggleDropdown() {
        if (this.dropdownOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        const dropdown = document.getElementById('languageDropdown');
        const button = document.querySelector('.current-language-btn');
        
        if (dropdown && button) {
            dropdown.classList.add('show');
            button.classList.add('open');
            this.dropdownOpen = true;
            
            console.log('📂 Dropdown opened');
        }
    }
    
    closeDropdown() {
        const dropdown = document.getElementById('languageDropdown');
        const button = document.querySelector('.current-language-btn');
        
        if (dropdown) {
            dropdown.classList.remove('show');
            button?.classList.remove('open');
            this.dropdownOpen = false;
            
            console.log('📁 Dropdown closed');
        }
    }
    
    async selectLanguage(langCode) {
        if (langCode === this.currentLanguage) {
            this.closeDropdown();
            return;
        }
        
        const language = this.availableLanguages[langCode];
        if (!language) {
            console.error('Language not found:', langCode);
            return;
        }
        
        console.log(`🌐 Switching to ${language.name}...`);
        
        try {
            // Show loading state
            this.showLoadingState();
            
            // Update UI immediately for responsive feel
            this.updateCurrentLanguageDisplay(langCode);
            
            // Save preference
            this.saveLanguagePreference(langCode);
            
            // Close dropdown
            this.closeDropdown();
            
            // Reload page with new language parameter
            await this.reloadWithLanguage(langCode);
            
        } catch (error) {
            console.error('Error switching language:', error);
            this.showNotification('Erreur lors du changement de langue', 'error');
            // Revert to previous language
            this.updateCurrentLanguageDisplay(this.currentLanguage);
            this.hideLoadingState();
        }
    }
    
    updateCurrentLanguageDisplay(langCode) {
        const language = this.availableLanguages[langCode];
        const flag = document.querySelector('.flag-current');
        const name = document.querySelector('.language-name');
        
        if (flag) {
            flag.src = `/static/img/country_flags/${language.flag}`;
            flag.alt = language.name;
        }
        
        if (name) {
            name.textContent = language.name;
        }
        
        // Update active state in dropdown
        document.querySelectorAll('.language-option').forEach(option => {
            option.classList.toggle('active', option.dataset.lang === langCode);
        });
        
        this.currentLanguage = langCode;
    }
    
    async reloadWithLanguage(langCode) {
        const language = this.availableLanguages[langCode];
        
        // Show loading notification
        this.showNotification(`Chargement du contenu en ${language.name}...`, 'info');
        
        // Get current URL and add/update language parameter
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('lang', langCode);
        
        // For now, reload the page with the language parameter
        // TODO: In the future, this could be replaced with an AJAX call to update content dynamically
        setTimeout(() => {
            window.location.href = currentUrl.toString();
        }, 800);
    }
    
    showLoadingState() {
        const button = document.querySelector('.current-language-btn');
        if (button) {
            button.style.opacity = '0.7';
            button.style.pointerEvents = 'none';
        }
    }
    
    hideLoadingState() {
        const button = document.querySelector('.current-language-btn');
        if (button) {
            button.style.opacity = '';
            button.style.pointerEvents = '';
        }
    }
    
    saveLanguagePreference(langCode) {
        localStorage.setItem('preferred_language', langCode);
        console.log(`💾 Language preference saved: ${langCode}`);
    }
    
    loadUserLanguagePreference() {
        // Check if there's a language from the URL parameter first
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        
        if (urlLang && this.availableLanguages[urlLang]) {
            this.currentLanguage = urlLang;
            this.updateCurrentLanguageDisplay(urlLang);
            this.saveLanguagePreference(urlLang);
            return;
        }
        
        // Otherwise check localStorage
        const saved = localStorage.getItem('preferred_language');
        if (saved && this.availableLanguages[saved]) {
            this.currentLanguage = saved;
            this.updateCurrentLanguageDisplay(saved);
        }
    }
    
    showNotification(message, type = 'info') {
        // Simple notification for now
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        const colors = {
            'success': '#10b981',
            'error': '#ef4444',
            'info': '#3b82f6'
        };
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type] || colors.info};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        const duration = type === 'info' ? 2000 : 3000;
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    /* Ensure dropdown transitions work - normal z-index since it's in app header */
    .language-dropdown {
        transition: all 200ms ease !important;
        z-index: 1001 !important;
    }
    
    .language-dropdown.show {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translateY(0) !important;
        z-index: 1001 !important;
    }
    
    .language-selector-header {
        z-index: 1000 !important;
        position: relative !important;
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
let languageSelector = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        languageSelector = new LanguageSelector();
        window.LanguageSelector = languageSelector;
    });
} else {
    languageSelector = new LanguageSelector();
    window.LanguageSelector = languageSelector;
}

// Global function for compatibility
window.toggleLanguageDropdown = function() {
    if (window.LanguageSelector) {
        window.LanguageSelector.toggleDropdown();
    }
};

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageSelector;
}