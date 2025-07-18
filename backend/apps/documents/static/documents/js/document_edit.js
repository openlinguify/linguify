/**
 * Document Editor JavaScript
 * Handles both markdown and rich text editing with real-time collaboration features
 */

class DocumentEditor {
    constructor() {
        this.documentId = document.getElementById('document-id')?.value;
        this.currentEditorType = 'html'; // Always HTML/visual mode
        this.autoSaveTimeout = null;
        this.autoSaveInterval = 3000; // 3 seconds
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.bindEvents();
        this.setupAutoSave();
        this.setupVisualToolbar();
        this.updateWordCount();
        
        this.isInitialized = true;
        console.log('Visual document editor initialized');
    }
    
    bindEvents() {
        // Save buttons
        document.getElementById('save-document')?.addEventListener('click', () => {
            this.saveDocument();
        });
        
        document.getElementById('save-draft')?.addEventListener('click', () => {
            this.saveDraft();
        });
        
        // Visual editor content change detection
        document.getElementById('visual-editor-content')?.addEventListener('input', () => {
            this.onContentChange();
            this.updateWordCount();
        });
        
        // Title change
        document.getElementById('document-title')?.addEventListener('input', () => {
            this.onContentChange();
        });
        
        // Metadata changes
        this.bindMetadataEvents();
        
        // Collaboration events
        this.bindCollaborationEvents();
        
        // Version events
        this.bindVersionEvents();
    }
    
    bindMetadataEvents() {
        ['document-folder', 'document-visibility', 'document-language', 
         'document-difficulty', 'document-tags'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', () => {
                this.onContentChange();
            });
        });
    }
    
    bindCollaborationEvents() {
        // Add collaborator
        document.getElementById('add-collaborator')?.addEventListener('click', () => {
            this.showAddCollaboratorModal();
        });
        
        // Remove collaborator
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="remove-share"]')) {
                const shareId = e.target.closest('.collaborator-item').dataset.shareId;
                this.removeCollaborator(shareId);
            }
        });
    }
    
    bindVersionEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="restore-version"]')) {
                const versionId = e.target.dataset.versionId;
                this.restoreVersion(versionId);
            }
        });
    }
    
    // Visual editor is always active - no switching needed
    
    getCurrentContent() {
        return document.getElementById('visual-editor-content')?.innerHTML || '';
    }
    
    setCurrentContent(content) {
        const editor = document.getElementById('visual-editor-content');
        if (editor) editor.innerHTML = content;
    }
    
    setupAutoSave() {
        // Auto-save will trigger after user stops typing for 3 seconds
        this.onContentChange();
    }
    
    onContentChange() {
        this.clearAutoSaveTimeout();
        this.autoSaveTimeout = setTimeout(() => {
            this.autoSave();
        }, this.autoSaveInterval);
    }
    
    clearAutoSaveTimeout() {
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = null;
        }
    }
    
    setupVisualToolbar() {
        const toolbar = document.querySelector('#visual-editor-container .editor-toolbar');
        if (!toolbar) return;
        
        toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('button[data-command]');
            if (!button) return;
            
            e.preventDefault();
            const command = button.dataset.command;
            this.executeVisualCommand(command);
        });
        
        toolbar.addEventListener('change', (e) => {
            const select = e.target.closest('select[data-command]');
            if (!select) return;
            
            const command = select.dataset.command;
            const value = select.value;
            this.executeVisualCommand(command, value);
        });
    }
    
    executeVisualCommand(command, value = null) {
        const editor = document.getElementById('visual-editor-content');
        if (!editor) return;
        
        editor.focus();
        
        try {
            if (command === 'createLink') {
                const url = prompt('URL du lien:');
                if (url) {
                    document.execCommand(command, false, url);
                }
            } else if (value) {
                document.execCommand(command, false, value);
            } else {
                document.execCommand(command, false, null);
            }
            
            this.onContentChange();
            this.updateWordCount();
        } catch (error) {
            console.error('Visual editor command error:', error);
        }
    }
    
    // No preview needed - WYSIWYG editor shows final result directly
    
    updateWordCount() {
        const content = this.getCurrentContent();
        
        // Extract text content from HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        const textContent = tempDiv.textContent || tempDiv.innerText || '';
        
        const words = textContent.trim() ? textContent.trim().split(/\s+/).length : 0;
        
        // Update word count display
        const visualWordCount = document.getElementById('visual-word-count');
        if (visualWordCount) visualWordCount.textContent = words;
    }
    
    // Content conversion not needed - visual editor works directly with HTML
    
    // Document saving methods
    async saveDocument() {
        const data = this.getDocumentData();
        return this.submitDocument(data, false);
    }
    
    async saveDraft() {
        const data = this.getDocumentData();
        return this.submitDocument(data, true);
    }
    
    async autoSave() {
        const data = this.getDocumentData();
        return this.submitDocument(data, true, true);
    }
    
    getDocumentData() {
        return {
            title: document.getElementById('document-title')?.value || '',
            content: this.getCurrentContent(),
            content_type: this.currentEditorType,
            folder: document.getElementById('document-folder')?.value || null,
            visibility: document.getElementById('document-visibility')?.value || 'private',
            language: document.getElementById('document-language')?.value || '',
            difficulty_level: document.getElementById('document-difficulty')?.value || '',
            tags: document.getElementById('document-tags')?.value || ''
        };
    }
    
    async submitDocument(data, isDraft = false, isAutoSave = false) {
        if (!this.documentId) {
            console.error('No document ID available');
            return;
        }
        
        const indicator = document.getElementById('auto-save-indicator');
        
        if (!isAutoSave) {
            indicator.textContent = 'Enregistrement...';
            indicator.className = 'auto-save-indicator';
        }
        
        try {
            const response = await fetch(`/documents/api/v1/documents/${this.documentId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (isAutoSave) {
                    indicator.textContent = 'Sauvegardé automatiquement';
                    indicator.className = 'auto-save-indicator success';
                    setTimeout(() => {
                        indicator.textContent = '';
                        indicator.className = 'auto-save-indicator';
                    }, 2000);
                } else {
                    this.showNotification(
                        isDraft ? 'Brouillon sauvegardé' : 'Document enregistré avec succès', 
                        'success'
                    );
                }
                
                return result;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Save error:', error);
            
            indicator.textContent = 'Erreur de sauvegarde';
            indicator.className = 'auto-save-indicator error';
            
            if (!isAutoSave) {
                this.showNotification('Erreur lors de l\'enregistrement', 'error');
            }
            
            setTimeout(() => {
                indicator.textContent = '';
                indicator.className = 'auto-save-indicator';
            }, 3000);
        }
    }
    
    // Collaboration methods
    showAddCollaboratorModal() {
        const email = prompt('Email de l\'utilisateur à ajouter:');
        if (email) {
            this.addCollaborator(email);
        }
    }
    
    async addCollaborator(email, permission = 'view') {
        try {
            const response = await fetch(`/documents/api/v1/documents/${this.documentId}/share/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    user_email: email,
                    permission_level: permission
                })
            });
            
            if (response.ok) {
                this.showNotification('Collaborateur ajouté avec succès', 'success');
                // Refresh collaborators list
                location.reload();
            } else {
                const error = await response.json();
                this.showNotification(error.message || 'Erreur lors de l\'ajout', 'error');
            }
        } catch (error) {
            console.error('Add collaborator error:', error);
            this.showNotification('Erreur lors de l\'ajout du collaborateur', 'error');
        }
    }
    
    async removeCollaborator(shareId) {
        if (!confirm('Êtes-vous sûr de vouloir retirer ce collaborateur ?')) {
            return;
        }
        
        try {
            const response = await fetch(`/documents/api/v1/shares/${shareId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (response.ok) {
                this.showNotification('Collaborateur retiré', 'success');
                // Remove from UI
                document.querySelector(`[data-share-id="${shareId}"]`)?.remove();
            } else {
                this.showNotification('Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('Remove collaborator error:', error);
            this.showNotification('Erreur lors de la suppression', 'error');
        }
    }
    
    // Version management
    async restoreVersion(versionId) {
        if (!confirm('Êtes-vous sûr de vouloir restaurer cette version ? Les modifications actuelles seront perdues.')) {
            return;
        }
        
        try {
            const response = await fetch(`/documents/api/v1/documents/${this.documentId}/restore_version/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    version_id: versionId
                })
            });
            
            if (response.ok) {
                this.showNotification('Version restaurée avec succès', 'success');
                location.reload();
            } else {
                this.showNotification('Erreur lors de la restauration', 'error');
            }
        } catch (error) {
            console.error('Restore version error:', error);
            this.showNotification('Erreur lors de la restauration', 'error');
        }
    }
    
    // Utility functions
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showNotification(message, type = 'info') {
        // Create toast notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1055; max-width: 400px;';
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Additional utility functions
function insertImage() {
    const url = prompt('URL de l\'image:');
    if (url) {
        document.execCommand('insertImage', false, url);
    }
}

// Initialize the document editor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.editor-page-container')) {
        new DocumentEditor();
    }
});

// Preview toggle for mobile
document.getElementById('toggle-preview')?.addEventListener('click', function() {
    const previewPane = document.querySelector('.preview-pane');
    previewPane.classList.toggle('show');
});