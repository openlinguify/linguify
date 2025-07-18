/**
 * Document Confirm Delete JavaScript
 * Linguify - Gestion de la suppression sécurisée des documents
 */

class DocumentDeleteConfirmation {
    constructor() {
        this.confirmUnderstanding = document.getElementById('confirm-understanding');
        this.confirmDelete = document.getElementById('confirm-delete');
        this.deleteButton = document.getElementById('delete-button');
        this.deleteForm = document.querySelector('.delete-form');
        this.documentId = this.getDocumentId();
        
        this.init();
    }
    
    /**
     * Initialise les événements et l'état initial
     */
    init() {
        if (!this.confirmUnderstanding || !this.confirmDelete || !this.deleteButton) {
            console.error('Elements requis pour la confirmation de suppression non trouvés');
            return;
        }
        
        this.bindEvents();
        this.updateDeleteButtonState();
        this.addVisualFeedback();
    }
    
    /**
     * Lie tous les événements nécessaires
     */
    bindEvents() {
        // Événements des checkboxes
        this.confirmUnderstanding.addEventListener('change', () => {
            this.updateDeleteButtonState();
            this.showProgressFeedback();
        });
        
        this.confirmDelete.addEventListener('change', () => {
            this.updateDeleteButtonState();
            this.showProgressFeedback();
        });
        
        // Prévention de soumission accidentelle
        this.deleteForm.addEventListener('submit', (e) => {
            this.handleFormSubmission(e);
        });
        
        // Raccourcis clavier de sécurité
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Avertissement avant fermeture de page
        window.addEventListener('beforeunload', (e) => {
            if (this.confirmUnderstanding.checked || this.confirmDelete.checked) {
                e.preventDefault();
                e.returnValue = 'Êtes-vous sûr de vouloir quitter cette page ?';
                return e.returnValue;
            }
        });
    }
    
    /**
     * Met à jour l'état du bouton de suppression
     */
    updateDeleteButtonState() {
        const bothChecked = this.confirmUnderstanding.checked && this.confirmDelete.checked;
        
        this.deleteButton.disabled = !bothChecked;
        
        // Mise à jour visuelle
        if (bothChecked) {
            this.deleteButton.classList.add('btn-danger-active');
            this.deleteButton.innerHTML = '<i class="bi bi-trash"></i> Supprimer définitivement';
        } else {
            this.deleteButton.classList.remove('btn-danger-active');
            this.deleteButton.innerHTML = '<i class="bi bi-lock"></i> Confirmations requises';
        }
    }
    
    /**
     * Affiche un feedback visuel de progression
     */
    showProgressFeedback() {
        const checkedCount = [this.confirmUnderstanding, this.confirmDelete]
            .filter(checkbox => checkbox.checked).length;
        
        const progressIndicator = document.querySelector('.confirmation-progress');
        if (!progressIndicator) {
            this.createProgressIndicator();
        }
        
        this.updateProgressIndicator(checkedCount);
    }
    
    /**
     * Crée un indicateur de progression
     */
    createProgressIndicator() {
        const finalConfirmation = document.querySelector('.final-confirmation');
        const progressHTML = `
            <div class="confirmation-progress mb-3">
                <div class="progress" style="height: 6px;">
                    <div class="progress-bar bg-danger" role="progressbar" style="width: 0%"></div>
                </div>
                <small class="text-muted mt-1 d-block">
                    <span class="progress-text">Complétez les confirmations pour activer la suppression</span>
                </small>
            </div>
        `;
        finalConfirmation.insertAdjacentHTML('afterbegin', progressHTML);
    }
    
    /**
     * Met à jour l'indicateur de progression
     */
    updateProgressIndicator(checkedCount) {
        const progressBar = document.querySelector('.progress-bar');
        const progressText = document.querySelector('.progress-text');
        
        if (!progressBar || !progressText) return;
        
        const percentage = (checkedCount / 2) * 100;
        progressBar.style.width = `${percentage}%`;
        
        const messages = [
            'Complétez les confirmations pour activer la suppression',
            'Une confirmation supplémentaire requise',
            'Suppression activée - soyez prudent!'
        ];
        
        progressText.textContent = messages[checkedCount];
        
        if (checkedCount === 2) {
            progressBar.classList.remove('bg-danger');
            progressBar.classList.add('bg-warning');
        }
    }
    
    /**
     * Gère la soumission du formulaire avec confirmations multiples
     */
    handleFormSubmission(e) {
        // Première confirmation - native browser
        if (!confirm('  ATTENTION: Êtes-vous absolument certain de vouloir supprimer ce document ?\n\nCette action ne peut pas être annulée.')) {
            e.preventDefault();
            return;
        }
        
        // Deuxième confirmation - custom
        if (!this.showFinalWarningModal()) {
            e.preventDefault();
            return;
        }
        
        // Affichage de l'état de chargement
        this.showLoadingState();
    }
    
    /**
     * Affiche une modal de confirmation finale
     */
    showFinalWarningModal() {
        const documentTitle = document.querySelector('.alert-danger h5').textContent.trim();
        
        return confirm(`=Ñ SUPPRESSION DÉFINITIVE\n\nDocument: "${documentTitle}"\n\n` +
                      `Cette action va:\n` +
                      `" Supprimer définitivement le document\n` +
                      `" Effacer tout l'historique des versions\n` +
                      `" Retirer l'accès à tous les collaborateurs\n` +
                      `" Supprimer tous les commentaires\n\n` +
                      `Confirmez-vous la suppression définitive ?`);
    }
    
    /**
     * Affiche l'état de chargement pendant la suppression
     */
    showLoadingState() {
        this.deleteButton.disabled = true;
        this.deleteButton.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Suppression en cours...
        `;
        
        // Désactive tous les autres boutons
        document.querySelectorAll('.btn').forEach(btn => {
            if (btn !== this.deleteButton) {
                btn.disabled = true;
            }
        });
        
        // Affiche un message de patience
        this.showDeletionProgress();
    }
    
    /**
     * Affiche la progression de suppression
     */
    showDeletionProgress() {
        const deleteCard = document.querySelector('.delete-card');
        const progressHTML = `
            <div class="deletion-progress mt-3 p-3 bg-danger bg-opacity-10 border border-danger rounded">
                <div class="d-flex align-items-center mb-2">
                    <div class="spinner-border spinner-border-sm text-danger me-2"></div>
                    <strong class="text-danger">Suppression en cours...</strong>
                </div>
                <div class="progress mb-2" style="height: 8px;">
                    <div class="progress-bar bg-danger progress-bar-striped progress-bar-animated" 
                         style="width: 100%"></div>
                </div>
                <small class="text-muted">
                    <i class="bi bi-info-circle me-1"></i>
                    Veuillez patienter, ne fermez pas cette page
                </small>
            </div>
        `;
        deleteCard.insertAdjacentHTML('beforeend', progressHTML);
    }
    
    /**
     * Gère les raccourcis clavier de sécurité
     */
    handleKeyboardShortcuts(e) {
        // Empêche Ctrl+S (sauvegarde accidentelle)
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            this.showWarning('Sauvegarde non disponible sur cette page');
        }
        
        // Empêche F5/Ctrl+R (rechargement accidentel)
        if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
            if (this.confirmUnderstanding.checked || this.confirmDelete.checked) {
                e.preventDefault();
                this.showWarning('Rechargement bloqué - confirmations en cours');
            }
        }
        
        // Echap pour annuler rapidement
        if (e.key === 'Escape') {
            this.quickCancel();
        }
    }
    
    /**
     * Annulation rapide avec Echap
     */
    quickCancel() {
        if (this.confirmUnderstanding.checked || this.confirmDelete.checked) {
            if (confirm('Annuler la suppression et revenir au document ?')) {
                window.location.href = this.getDocumentDetailUrl();
            }
        }
    }
    
    /**
     * Ajoute un feedback visuel aux interactions
     */
    addVisualFeedback() {
        // Animation sur les checkboxes
        [this.confirmUnderstanding, this.confirmDelete].forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const parent = e.target.closest('.form-check');
                if (e.target.checked) {
                    parent.classList.add('confirmed');
                    this.animateCheckmark(e.target);
                } else {
                    parent.classList.remove('confirmed');
                }
            });
        });
        
        // Effet hover sur le bouton de suppression
        this.deleteButton.addEventListener('mouseenter', () => {
            if (!this.deleteButton.disabled) {
                this.showDangerTooltip();
            }
        });
    }
    
    /**
     * Animation de validation pour les checkboxes
     */
    animateCheckmark(checkbox) {
        checkbox.style.transform = 'scale(1.1)';
        setTimeout(() => {
            checkbox.style.transform = 'scale(1)';
        }, 150);
    }
    
    /**
     * Affiche un tooltip de danger
     */
    showDangerTooltip() {
        const tooltip = document.createElement('div');
        tooltip.className = 'danger-tooltip';
        tooltip.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Action irréversible';
        
        this.deleteButton.appendChild(tooltip);
        
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.remove();
            }
        }, 2000);
    }
    
    /**
     * Affiche un message d'avertissement temporaire
     */
    showWarning(message) {
        const warning = document.createElement('div');
        warning.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        warning.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
        warning.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(warning);
        
        setTimeout(() => {
            if (warning.parentNode) {
                warning.remove();
            }
        }, 5000);
    }
    
    /**
     * Récupère l'ID du document depuis l'URL ou les données
     */
    getDocumentId() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput && csrfInput.form) {
            const action = csrfInput.form.action;
            const match = action.match(/\/documents\/(\d+)\//);
            return match ? match[1] : null;
        }
        return null;
    }
    
    /**
     * Génère l'URL de détail du document
     */
    getDocumentDetailUrl() {
        return this.documentId ? `/documents/${this.documentId}/` : '/documents/';
    }
}

/**
 * Fonctions utilitaires pour les actions alternatives
 */
class AlternativeActions {
    static async makePrivate() {
        if (!confirm('Rendre ce document privé au lieu de le supprimer ?\n\nCela retirera l\'accès à tous les collaborateurs.')) {
            return;
        }
        
        try {
            const documentId = new DocumentDeleteConfirmation().documentId;
            const response = await fetch(`/documents/api/v1/documents/${documentId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    visibility: 'private'
                })
            });
            
            if (response.ok) {
                AlternativeActions.showSuccess('Document rendu privé avec succès');
                setTimeout(() => {
                    window.location.href = `/documents/${documentId}/`;
                }, 1500);
            } else {
                throw new Error('Erreur serveur');
            }
        } catch (error) {
            console.error('Error:', error);
            AlternativeActions.showError('Erreur lors de la modification du document');
        }
    }
    
    static async removeCollaborators() {
        if (!confirm('Retirer tous les collaborateurs de ce document ?\n\nLe document restera actif mais sera accessible uniquement par vous.')) {
            return;
        }
        
        try {
            const documentId = new DocumentDeleteConfirmation().documentId;
            const response = await fetch(`/documents/api/v1/documents/${documentId}/collaborators/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            if (response.ok) {
                AlternativeActions.showSuccess('Tous les collaborateurs ont été retirés');
                setTimeout(() => {
                    window.location.href = `/documents/${documentId}/`;
                }, 1500);
            } else {
                throw new Error('Erreur serveur');
            }
        } catch (error) {
            console.error('Error:', error);
            AlternativeActions.showError('Fonctionnalité à implémenter côté serveur');
        }
    }
    
    static showSuccess(message) {
        AlternativeActions.showNotification(message, 'success');
    }
    
    static showError(message) {
        AlternativeActions.showNotification(message, 'danger');
    }
    
    static showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1055; max-width: 400px;';
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

/**
 * Initialisation au chargement de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialise la gestion de confirmation de suppression
    new DocumentDeleteConfirmation();
    
    // Expose les fonctions alternatives globalement pour les boutons onclick
    window.makePrivate = AlternativeActions.makePrivate;
    window.removeCollaborators = AlternativeActions.removeCollaborators;
    
    // Ajoute des styles CSS dynamiques pour les effets
    const style = document.createElement('style');
    style.textContent = `
        .form-check.confirmed {
            background-color: rgba(239, 68, 68, 0.1);
            border-color: var(--linguify-error);
            transform: scale(1.02);
            transition: all 0.2s ease;
        }
        
        .btn-danger-active {
            animation: pulse-danger 2s infinite;
        }
        
        @keyframes pulse-danger {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        }
        
        .danger-tooltip {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #dc3545;
            color: white;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            white-space: nowrap;
            z-index: 1000;
            margin-bottom: 0.5rem;
        }
        
        .danger-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #dc3545;
        }
    `;
    document.head.appendChild(style);
});

/**
 * Export pour utilisation en module si nécessaire
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DocumentDeleteConfirmation, AlternativeActions };
}