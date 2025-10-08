/* App Store JavaScript for Open Linguify */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const categoryButtons = document.querySelectorAll('.category-item');
    const searchInput = document.getElementById('searchInput');
    const appsGrid = document.getElementById('appsGrid');
    const emptyState = document.getElementById('emptyState');
    const toggleInputs = document.querySelectorAll('.install-toggle input[type="checkbox"]');
    
    // Current filter
    let currentCategory = 'all';
    let currentSearch = '';
    
    // Category filtering
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.dataset.category;
            filterApps();
        });
    });
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            currentSearch = this.value.toLowerCase();
            filterApps();
        });
    }
    
    // Filter apps function
    function filterApps() {
        const appCards = document.querySelectorAll('.app-card');
        let visibleCount = 0;
        
        appCards.forEach(card => {
            const category = card.dataset.category || '';
            const title = card.querySelector('.app-title').textContent;
            const titleLower = title.toLowerCase();
            const description = card.querySelector('.app-description').textContent.toLowerCase();
            
            // Category matching avec correspondance exacte (pas d'includes)
            let matchesCategory = currentCategory === 'all';
            if (!matchesCategory) {
                // Correspondance exacte avec les catégories du backend
                matchesCategory = category === currentCategory;
            }
            
            const matchesSearch = currentSearch === '' || 
                                titleLower.includes(currentSearch) || 
                                description.includes(currentSearch);
            
            const shouldShow = matchesCategory && matchesSearch;
            
            if (shouldShow) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show/hide empty state
        if (visibleCount === 0 && appsGrid) {
            appsGrid.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
        } else if (appsGrid) {
            appsGrid.style.display = 'grid';
            if (emptyState) emptyState.style.display = 'none';
        }
    }
    
    // Toggle functionality
    toggleInputs.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const appId = this.dataset.appId;
            const isInstalling = this.checked;
            const card = this.closest('.app-card');
            
            // Si on désinstalle, montrer la modal de confirmation
            if (!isInstalling) {
                showUninstallModal(appId, this, card);
                return;
            }
            
            // Sinon, installer directement
            toggleApp(appId, this, card, isInstalling);
        });
    });
    
    function showUninstallModal(appId, toggle, card) {
        // Remettre le toggle en position "on" temporairement
        toggle.checked = true;
        
        // Récupérer les infos de l'app avec vérification de sécurité
        const appTitleElement = card.querySelector('.app-title');
        const appName = appTitleElement ? appTitleElement.textContent : 'Application';
        
        // Gérer les nouvelles icônes IMG ou les anciennes icônes I
        const appIconImg = card.querySelector('.app-icon img');
        const appIconI = card.querySelector('.app-icon i');
        
        let appIcon = '';
        if (appIconImg) {
            // Nouvelle structure avec images
            appIcon = appIconImg.src;
        } else if (appIconI) {
            // Ancienne structure avec icônes Bootstrap
            appIcon = appIconI.className;
        }
        
        const appIconElement = card.querySelector('.app-icon');
        const appIconBg = appIconElement ? appIconElement.style.background : 'transparent';
        
        // Configurer la modal
        const modal = document.getElementById('uninstallModal');
        const modalAppName = document.getElementById('modalAppName');
        const modalAppIcon = document.getElementById('modalAppIcon');
        const confirmButton = document.getElementById('confirmUninstall');
        
        // Mettre à jour le contenu de la modal
        modalAppName.textContent = appName;
        
        // Afficher l'icône appropriée dans la modal (SÉCURISÉ)
        if (appIconImg) {
            // Nouvelle structure avec images - sanitize URL
            const sanitizedIcon = appIcon.replace(/[<>"']/g, '');
            const sanitizedName = appName.replace(/[<>"']/g, '');
            modalAppIcon.innerHTML = `<img src="${sanitizedIcon}" alt="${sanitizedName} icon" style="width: 40px; height: 40px; object-fit: contain;">`;
        } else if (appIconI) {
            // Ancienne structure avec icônes Bootstrap - sanitize class
            const sanitizedClass = appIcon.replace(/[<>"']/g, '').replace(/[^a-zA-Z0-9\-_\s]/g, '');
            modalAppIcon.innerHTML = `<i class="${sanitizedClass}"></i>`;
        } else {
            // Fallback
            modalAppIcon.innerHTML = `<i class="bi bi-app"></i>`;
        }
        
        modalAppIcon.style.background = appIconBg;
        
        // Gérer la confirmation
        const handleConfirm = () => {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();
            toggleApp(appId, toggle, card, false);
            confirmButton.removeEventListener('click', handleConfirm);
        };
        
        // Gérer l'annulation
        const handleCancel = () => {
            toggle.checked = true; // Remettre en position "installé"
            confirmButton.removeEventListener('click', handleConfirm);
        };
        
        confirmButton.addEventListener('click', handleConfirm);
        modal.addEventListener('hidden.bs.modal', handleCancel, { once: true });
        
        // Montrer la modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    function toggleApp(appId, toggleInput, card, isInstalling) {
        // Show loading
        const loadingOverlay = card.querySelector('.loading-overlay');
        const statusDiv = card.querySelector('.install-status');
        const openButton = card.querySelector('.btn');
        
        loadingOverlay.style.display = 'flex';
        card.classList.add('installing');
        
        // Get toggle URL from data attribute
        const toggleUrl = document.querySelector('[data-toggle-url]')?.dataset.toggleUrl || `/api/app-manager/apps/${appId}/toggle/`;
        
        fetch(toggleUrl.replace('0', appId), {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update toggle state based on actual server response
                toggleInput.checked = data.is_enabled;
                
                // Update status
                statusDiv.className = `install-status ${data.is_enabled ? 'installed' : ''}`;
                statusDiv.innerHTML = data.is_enabled ? 
                    '<i class="bi bi-check-circle me-1"></i>Installée' : 
                    '<i class="bi bi-download me-1"></i>Non installée';
                
                // Update open button
                const footer = card.querySelector('.app-footer');
                if (data.is_enabled && !openButton) {
                    footer.innerHTML += `
                        <a href="#" class="btn btn-primary btn-sm">
                            <i class="bi bi-box-arrow-up-right me-1"></i>Ouvrir
                        </a>
                    `;
                } else if (!data.is_enabled && openButton) {
                    openButton.remove();
                }
                
                // Show success message with data retention info for uninstall
                let message = data.message;
                if (!isInstalling && window.appStoreTranslations) {
                    message += '. ' + window.appStoreTranslations.dataRetentionMessage;
                }
                
                showToast(message, 'success');
            } else {
                // Revert toggle on error
                toggleInput.checked = !isInstalling;
                throw new Error(data.error || 'Erreur lors de l\'opération');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toggleInput.checked = !isInstalling;
            showToast('Erreur lors de l\'opération', 'error');
        })
        .finally(() => {
            loadingOverlay.style.display = 'none';
            card.classList.remove('installing');
        });
    }
    
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) return csrfInput.value;
        
        const csrfCookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        if (csrfCookie) return csrfCookie.split('=')[1];
        
        return '';
    }
    
    function showToast(message, type) {
        const toastContainer = document.querySelector('.toast-container');
        const isSuccess = type === 'success';

        const toast = document.createElement('div');
        toast.className = `toast ${isSuccess ? 'bg-success' : 'bg-danger'} text-white`;

        // SÉCURISÉ: Créer les éléments DOM au lieu d'innerHTML
        const toastBody = document.createElement('div');
        toastBody.className = 'toast-body d-flex align-items-center';

        const icon = document.createElement('i');
        icon.className = `bi ${isSuccess ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'} me-2`;

        const messageText = document.createTextNode(message);

        toastBody.appendChild(icon);
        toastBody.appendChild(messageText);
        toast.appendChild(toastBody);
        
        toastContainer.appendChild(toast);
        
        // Show toast with Bootstrap
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 3000
            });
            bsToast.show();
            
            // Remove after hiding
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        } else {
            // Fallback without Bootstrap
            toast.style.opacity = '1';
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
    }
    
    // Mettre à jour les compteurs de catégories avec correspondance exacte
    function updateCategoryCounts() {
        const appCards = document.querySelectorAll('.app-card');
        const counts = {
            all: appCards.length,
            productivity: 0,
            communication: 0,
            social: 0,
            education: 0,
            collaboration: 0,
            ai: 0
        };
        
        appCards.forEach(card => {
            const category = card.dataset.category || '';
            
            // Correspondance exacte avec les vraies catégories du backend
            if (counts.hasOwnProperty(category)) {
                counts[category]++;
            }
        });
        
        // Mettre à jour les compteurs dans l'interface
        Object.keys(counts).forEach(cat => {
            const elem = document.getElementById(`count-${cat}`);
            if (elem) elem.textContent = counts[cat];
        });
    }
    
    // Appeler la fonction au chargement pour initialiser les compteurs
    updateCategoryCounts();
});