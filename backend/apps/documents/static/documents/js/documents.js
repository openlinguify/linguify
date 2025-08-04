/**
 * Documents App JavaScript
 * Handles document management functionality
 */

class DocumentsApp {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.initializeComponents();
    }
    
    bindEvents() {
        // Search functionality
        this.bindSearchEvents();
        
        // Document actions
        this.bindDocumentActions();
        
        // Folder management
        this.bindFolderActions();
        
        // Sharing functionality
        this.bindSharingActions();
        
        // Card interactions
        this.bindCardInteractions();
    }
    
    bindSearchEvents() {
        const searchInput = document.querySelector('#document-search');
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }
    }
    
    bindDocumentActions() {
        // Delete confirmation
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="delete-document"]')) {
                e.preventDefault();
                this.confirmDeleteDocument(e.target);
            }
            
            // Duplicate document
            if (e.target.matches('[data-action="duplicate-document"]')) {
                e.preventDefault();
                this.duplicateDocument(e.target);
            }
            
            // Export document
            if (e.target.matches('[data-action="export-document"]')) {
                e.preventDefault();
                this.exportDocument(e.target);
            }
        });
    }
    
    bindFolderActions() {
        // Create folder
        const createFolderBtn = document.querySelector('#create-folder-btn');
        if (createFolderBtn) {
            createFolderBtn.addEventListener('click', () => {
                this.showCreateFolderModal();
            });
        }
        
        // Move to folder
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-action="move-to-folder"]')) {
                this.moveDocumentToFolder(e.target);
            }
        });
    }
    
    bindSharingActions() {
        // Share document
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="share-document"]')) {
                e.preventDefault();
                this.showShareModal(e.target);
            }
            
            // Remove share
            if (e.target.matches('[data-action="remove-share"]')) {
                e.preventDefault();
                this.removeShare(e.target);
            }
        });
    }
    
    bindCardInteractions() {
        // Documents cards cliquables
        document.querySelectorAll('.document-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Éviter le clic si on clique sur le menu dropdown ou les actions
                if (e.target.closest('.dropdown') || 
                    e.target.closest('.document-actions') ||
                    e.target.closest('button') ||
                    e.target.closest('a')) {
                    return;
                }
                
                const link = card.querySelector('.document-content h3 a');
                if (link) {
                    window.location.href = link.href;
                }
            });
        });
        
        // Folder cards cliquables
        document.querySelectorAll('.folder-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Éviter le clic si on clique sur un bouton ou lien existant
                if (e.target.closest('button') || 
                    e.target.closest('a') ||
                    e.target.closest('.dropdown')) {
                    return;
                }
                
                const link = card.querySelector('.folder-content h4 a');
                if (link) {
                    window.location.href = link.href;
                }
            });
        });
        
        // Shared documents cliquables
        document.querySelectorAll('.shared-document-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Éviter le clic si on clique sur les actions
                if (e.target.closest('.document-actions') ||
                    e.target.closest('button') ||
                    e.target.closest('a')) {
                    return;
                }
                
                const link = item.querySelector('.document-details h4 a');
                if (link) {
                    window.location.href = link.href;
                }
            });
        });
        
        // Stat cards cliquables (navigation vers les listes)
        document.querySelectorAll('.stat-card').forEach(card => {
            const label = card.querySelector('.stat-label')?.textContent?.trim();
            
            if (label) {
                card.style.cursor = 'pointer';
                
                card.addEventListener('click', (e) => {
                    if (e.target.closest('button') || e.target.closest('a')) {
                        return;
                    }
                    
                    // Navigation basée sur le type de stat
                    if (label.includes('Documents')) {
                        window.location.href = '/documents/list/';
                    } else if (label.includes('Dossiers')) {
                        window.location.href = '/documents/folders/';
                    } else if (label.includes('Partagés')) {
                        window.location.href = '/documents/list/?shared=true';
                    }
                });
            }
        });
    }
    
    initializeComponents() {
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize drag and drop
        this.initializeDragDrop();
        
        // Initialize auto-save
        this.initializeAutoSave();
    }
    
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    initializeDragDrop() {
        // Drag and drop for organizing documents
        const documentCards = document.querySelectorAll('.document-card');
        const folderCards = document.querySelectorAll('.folder-card');
        
        documentCards.forEach(card => {
            card.draggable = true;
            card.addEventListener('dragstart', this.handleDragStart.bind(this));
        });
        
        folderCards.forEach(folder => {
            folder.addEventListener('dragover', this.handleDragOver.bind(this));
            folder.addEventListener('drop', this.handleDrop.bind(this));
        });
    }
    
    initializeAutoSave() {
        // Auto-save for document editor
        const contentArea = document.querySelector('#document-content');
        if (contentArea) {
            let saveTimeout;
            
            contentArea.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    this.autoSaveDocument();
                }, 2000);
            });
        }
    }
    
    // Search functionality
    performSearch(query) {
        if (query.length < 2) {
            this.clearSearchResults();
            return;
        }
        
        fetch(`/documents/api/v1/documents/?search=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            this.displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
            this.showNotification('Erreur lors de la recherche', 'error');
        });
    }
    
    displaySearchResults(results) {
        const container = document.querySelector('#search-results');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (results.length === 0) {
            container.innerHTML = '<div class="search-no-results">Aucun résultat trouvé</div>';
            return;
        }
        
        results.forEach(doc => {
            const item = this.createSearchResultItem(doc);
            container.appendChild(item);
        });
    }
    
    createSearchResultItem(document) {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
            <div class="search-result-content">
                <h4><a href="/documents/${document.id}/">${document.title}</a></h4>
                <p>${document.folder_name || 'Sans dossier'}</p>
                <div class="search-result-meta">
                    <span>Modifié ${this.formatDate(document.updated_at)}</span>
                </div>
            </div>
        `;
        return item;
    }
    
    clearSearchResults() {
        const container = document.querySelector('#search-results');
        if (container) {
            container.innerHTML = '';
        }
    }
    
    // Document actions
    confirmDeleteDocument(button) {
        const documentTitle = button.dataset.documentTitle;
        const documentId = button.dataset.documentId;
        
        if (confirm(`Êtes-vous sûr de vouloir supprimer "${documentTitle}" ?`)) {
            this.deleteDocument(documentId);
        }
    }
    
    deleteDocument(documentId) {
        fetch(`/documents/api/v1/documents/${documentId}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'X-CSRFToken': this.getCsrfToken()
            }
        })
        .then(response => {
            if (response.ok) {
                this.showNotification('Document supprimé avec succès', 'success');
                // Remove from UI or redirect
                window.location.href = '/documents/';
            } else {
                throw new Error('Erreur lors de la suppression');
            }
        })
        .catch(error => {
            console.error('Delete error:', error);
            this.showNotification('Erreur lors de la suppression', 'error');
        });
    }
    
    duplicateDocument(button) {
        const documentId = button.dataset.documentId;
        
        fetch(`/documents/api/v1/documents/${documentId}/duplicate/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'X-CSRFToken': this.getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            this.showNotification('Document dupliqué avec succès', 'success');
            // Redirect to new document
            window.location.href = `/documents/${data.id}/`;
        })
        .catch(error => {
            console.error('Duplicate error:', error);
            this.showNotification('Erreur lors de la duplication', 'error');
        });
    }
    
    exportDocument(button) {
        const documentId = button.dataset.documentId;
        const format = button.dataset.format || 'markdown';
        
        fetch(`/documents/api/v1/documents/${documentId}/export/?format=${format}`, {
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`
            }
        })
        .then(response => response.json())
        .then(data => {
            this.downloadFile(data.content, `${data.title}.${format}`, data.content_type);
        })
        .catch(error => {
            console.error('Export error:', error);
            this.showNotification('Erreur lors de l\'export', 'error');
        });
    }
    
    // Folder management
    showCreateFolderModal() {
        // Implementation depends on your modal system
        // This is a placeholder
        const name = prompt('Nom du dossier:');
        if (name) {
            this.createFolder(name);
        }
    }
    
    createFolder(name, description = '') {
        fetch('/documents/api/v1/folders/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        })
        .then(response => response.json())
        .then(data => {
            this.showNotification('Dossier créé avec succès', 'success');
            // Refresh page or update UI
            location.reload();
        })
        .catch(error => {
            console.error('Create folder error:', error);
            this.showNotification('Erreur lors de la création du dossier', 'error');
        });
    }
    
    moveDocumentToFolder(select) {
        const documentId = select.dataset.documentId;
        const folderId = select.value;
        
        fetch(`/documents/api/v1/documents/${documentId}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                folder: folderId || null
            })
        })
        .then(response => response.json())
        .then(data => {
            this.showNotification('Document déplacé avec succès', 'success');
        })
        .catch(error => {
            console.error('Move document error:', error);
            this.showNotification('Erreur lors du déplacement', 'error');
        });
    }
    
    // Drag and drop handlers
    handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.documentId);
        e.target.classList.add('dragging');
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.target.classList.add('drag-over');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.target.classList.remove('drag-over');
        
        const documentId = e.dataTransfer.getData('text/plain');
        const folderId = e.target.dataset.folderId;
        
        if (documentId && folderId) {
            this.moveDocumentToFolder({
                dataset: { documentId: documentId },
                value: folderId
            });
        }
    }
    
    // Auto-save functionality
    autoSaveDocument() {
        const documentId = document.querySelector('#document-id')?.value;
        const content = document.querySelector('#document-content')?.value;
        
        if (!documentId || !content) return;
        
        fetch(`/documents/api/v1/documents/${documentId}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                content: content
            })
        })
        .then(response => {
            if (response.ok) {
                this.showAutoSaveIndicator();
            }
        })
        .catch(error => {
            console.error('Auto-save error:', error);
        });
    }
    
    showAutoSaveIndicator() {
        const indicator = document.querySelector('#auto-save-indicator');
        if (indicator) {
            indicator.textContent = 'Sauvegardé automatiquement';
            indicator.className = 'auto-save-indicator success';
            
            setTimeout(() => {
                indicator.textContent = '';
                indicator.className = 'auto-save-indicator';
            }, 2000);
        }
    }
    
    // Utility functions
    getAuthToken() {
        // Implement based on your auth system
        return localStorage.getItem('authToken') || '';
    }
    
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }
    
    downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    showNotification(message, type = 'info') {
        // Implementation depends on your notification system
        // This is a simple alert fallback
        if (type === 'error') {
            alert('Erreur: ' + message);
        } else {
            console.log(message);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentsApp();
});