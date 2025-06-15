/* App Store JavaScript for Open Linguify */

class AppStore {
    constructor() {
        this.apps = [];
        this.userSettings = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.isLoading = false;

        this.init();
    }

    async init() {
        await this.loadApps();
        await this.loadUserSettings();
        this.setupEventListeners();
        this.renderApps();
        this.updateCategoryCounts();
    }

    async loadApps() {
        try {
            const response = await fetch('/api/v1/app-manager/apps/');
            const data = await response.json();
            this.apps = data;
        } catch (error) {
            console.error('Erreur lors du chargement des apps:', error);
            this.showToast('Erreur lors du chargement des applications', 'error');
        }
    }

    async loadUserSettings() {
        try {
            const response = await fetch('/api/v1/app-manager/enabled/');
            const data = await response.json();
            this.userSettings = data.enabled_app_codes || [];
        } catch (error) {
            console.error('Erreur lors du chargement des paramètres utilisateur:', error);
        }
    }

    setupEventListeners() {
        // Category filter
        document.querySelectorAll('.category-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.category-item').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentCategory = btn.dataset.category;
                this.renderApps();
            });
        });

        // Search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.renderApps();
            });
        }
    }

    renderApps() {
        const grid = document.getElementById('appsGrid');
        const emptyState = document.getElementById('emptyState');
        
        if (!grid) return;

        // Filter apps
        let filteredApps = this.apps;
        
        if (this.currentCategory !== 'all') {
            filteredApps = filteredApps.filter(app => 
                app.category.toLowerCase().replace(' ', '_') === this.currentCategory
            );
        }
        
        if (this.searchQuery) {
            filteredApps = filteredApps.filter(app => 
                app.display_name.toLowerCase().includes(this.searchQuery) || 
                app.description.toLowerCase().includes(this.searchQuery)
            );
        }

        // Clear grid
        grid.innerHTML = '';

        if (filteredApps.length === 0) {
            grid.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        grid.style.display = 'grid';
        if (emptyState) emptyState.style.display = 'none';

        // Render each app
        filteredApps.forEach(app => {
            const appCard = this.createAppCard(app);
            grid.appendChild(appCard);
        });
    }

    createAppCard(app) {
        const isInstalled = this.userSettings.includes(app.code);
        const iconMapping = this.getIconMapping();
        const icon = iconMapping[app.manifest_data?.frontend_components?.icon] || 'bi-app';
        const colorMapping = this.getColorMapping();
        const color = colorMapping[app.display_name.toLowerCase()] || 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)';

        const card = document.createElement('div');
        card.className = 'app-card';
        card.innerHTML = `
            <div class="app-header">
                <div class="app-icon" style="background: ${color};">
                    <i class="bi ${icon}"></i>
                </div>
                <div class="app-info">
                    <h6 class="app-title">${app.display_name}</h6>
                    <div class="app-category">${app.category}</div>
                </div>
            </div>
            <p class="app-description">${app.description}</p>
            <div class="app-footer">
                <span class="install-status ${isInstalled ? 'installed' : ''}">
                    ${isInstalled ? 'Installé' : 'Non installé'}
                </span>
                <label class="install-toggle">
                    <input type="checkbox" ${isInstalled ? 'checked' : ''} 
                           onchange="appStore.toggleApp('${app.code}', this)">
                    <span class="install-toggle-slider"></span>
                </label>
            </div>
        `;

        // Click on card opens app if installed
        if (isInstalled && app.manifest_data?.technical_info?.web_url) {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.install-toggle')) {
                    window.location.href = app.manifest_data.technical_info.web_url;
                }
            });
        }

        return card;
    }

    async toggleApp(appCode, toggle) {
        if (this.isLoading) return;

        const app = this.apps.find(a => a.code === appCode);
        if (!app) return;

        const card = toggle.closest('.app-card');
        
        // Show loading
        this.showLoading(card);
        this.isLoading = true;

        try {
            const response = await fetch('/api/v1/app-manager/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    app_code: appCode,
                    enabled: toggle.checked
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Update user settings
                if (toggle.checked) {
                    if (!this.userSettings.includes(appCode)) {
                        this.userSettings.push(appCode);
                    }
                } else {
                    this.userSettings = this.userSettings.filter(code => code !== appCode);
                }

                // Update status text
                const statusText = card.querySelector('.install-status');
                statusText.textContent = toggle.checked ? 'Installé' : 'Non installé';
                statusText.classList.toggle('installed', toggle.checked);
                
                // Update card behavior
                if (toggle.checked && app.manifest_data?.technical_info?.web_url) {
                    card.style.cursor = 'pointer';
                    card.onclick = (e) => {
                        if (!e.target.closest('.install-toggle')) {
                            window.location.href = app.manifest_data.technical_info.web_url;
                        }
                    };
                } else {
                    card.style.cursor = 'default';
                    card.onclick = null;
                }
                
                // Show success message
                this.showToast(toggle.checked ? 
                    `${app.display_name} a été installé avec succès` : 
                    `${app.display_name} a été désinstallé`, 
                    'success'
                );
            } else {
                // Revert toggle on error
                toggle.checked = !toggle.checked;
                this.showToast(data.message || 'Une erreur est survenue', 'error');
            }
        } catch (error) {
            console.error('Erreur lors du toggle de l\'app:', error);
            toggle.checked = !toggle.checked;
            this.showToast('Erreur de connexion', 'error');
        } finally {
            this.hideLoading(card);
            this.isLoading = false;
        }
    }

    updateCategoryCounts() {
        const counts = {
            all: this.apps.length,
            learning: this.apps.filter(a => 
                a.category.toLowerCase().includes('apprentissage') || 
                a.category.toLowerCase().includes('learning') ||
                a.category.toLowerCase().includes('education')
            ).length,
            productivity: this.apps.filter(a => 
                a.category.toLowerCase().includes('productivité') || 
                a.category.toLowerCase().includes('productivity')
            ).length,
            ai: this.apps.filter(a => 
                a.category.toLowerCase().includes('ia') || 
                a.category.toLowerCase().includes('intelligence') ||
                a.category.toLowerCase().includes('ai')
            ).length
        };

        Object.keys(counts).forEach(cat => {
            const elem = document.getElementById(`count-${cat}`);
            if (elem) elem.textContent = counts[cat];
        });
    }

    showLoading(card) {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        card.style.position = 'relative';
        card.appendChild(loadingOverlay);
        card.classList.add('installing');
    }

    hideLoading(card) {
        const loadingOverlay = card.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
        card.classList.remove('installing');
    }

    showToast(message, type = 'success') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toast = document.createElement('div');
        const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        const iconClass = type === 'error' ? 'bi-exclamation-triangle' : 'bi-check-circle';
        
        toast.className = `alert ${alertClass} alert-dismissible fade show toast`;
        toast.innerHTML = `
            <i class="bi ${iconClass} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        toastContainer.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 150);
        }, 4000);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    getIconMapping() {
        return {
            '📓': 'bi-journal-text',
            '📚': 'bi-book',
            '🃏': 'bi-collection',
            '🤖': 'bi-robot',
            '📊': 'bi-graph-up',
            '🎯': 'bi-bullseye',
            '💬': 'bi-chat-dots',
            '❓': 'bi-patch-question'
        };
    }

    getColorMapping() {
        return {
            'notebook': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'cours': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'révision': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'revision': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'ia': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'language ai': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'assistant ia': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'quiz': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'quizz': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'chat': 'linear-gradient(135deg, #ec4899 0%, #d946ef 100%)'
        };
    }
}

// Initialize App Store when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.appStore = new AppStore();
});

// Export for use in other scripts
window.AppStore = AppStore;