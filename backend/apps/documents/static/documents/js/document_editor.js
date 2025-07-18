/**
 * Document Editor JavaScript
 * Handles both markdown and rich text editing with real-time collaboration features
 */

class DocumentEditor {
    constructor() {
        this.documentId = document.getElementById('document-id')?.value;
        this.currentEditorType = 'markdown';
        this.autoSaveTimeout = null;
        this.autoSaveInterval = 3000; // 3 seconds
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.bindEvents();
        this.setupEditorToggle();
        this.setupAutoSave();
        this.setupToolbars();
        this.updatePreview();
        
        this.isInitialized = true;
        console.log('Document editor initialized');
    }
    
    bindEvents() {
        // Save buttons
        document.getElementById('save-document')?.addEventListener('click', () => {
            this.saveDocument();
        });
        
        document.getElementById('save-draft')?.addEventListener('click', () => {
            this.saveDraft();
        });
        
        // Editor type toggle
        document.querySelectorAll('input[name="editor-type"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.switchEditor(e.target.value);
            });
        });
        
        // Content change detection
        document.getElementById('markdown-content')?.addEventListener('input', () => {
            this.onContentChange();
            this.updatePreview();
        });
        
        document.getElementById('rich-text-content')?.addEventListener('input', () => {
            this.onContentChange();
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
    
    setupEditorToggle() {
        const markdownRadio = document.getElementById('markdown-editor');
        const richTextRadio = document.getElementById('rich-text-editor');
        
        if (markdownRadio?.checked) {
            this.currentEditorType = 'markdown';
        } else if (richTextRadio?.checked) {
            this.currentEditorType = 'html';
        }
        
        this.showCurrentEditor();
    }
    
    switchEditor(editorType) {
        if (this.currentEditorType === editorType) return;
        
        // Get current content
        const currentContent = this.getCurrentContent();
        
        // Convert content if needed
        let convertedContent = currentContent;
        if (this.currentEditorType === 'markdown' && editorType === 'html') {
            convertedContent = this.markdownToHtml(currentContent);
        } else if (this.currentEditorType === 'html' && editorType === 'markdown') {
            convertedContent = this.htmlToMarkdown(currentContent);
        }
        
        // Switch editors
        this.currentEditorType = editorType;
        this.showCurrentEditor();
        this.setCurrentContent(convertedContent);
        
        // Update preview
        if (editorType === 'markdown') {
            this.updatePreview();
        }
    }
    
    showCurrentEditor() {
        const markdownContainer = document.getElementById('markdown-editor-container');
        const richTextContainer = document.getElementById('rich-text-editor-container');
        
        if (this.currentEditorType === 'markdown') {
            markdownContainer.style.display = 'flex';
            richTextContainer.style.display = 'none';
        } else {
            markdownContainer.style.display = 'none';
            richTextContainer.style.display = 'flex';
        }
    }
    
    getCurrentContent() {
        if (this.currentEditorType === 'markdown') {
            return document.getElementById('markdown-content')?.value || '';
        } else {
            return document.getElementById('rich-text-content')?.innerHTML || '';
        }
    }
    
    setCurrentContent(content) {
        if (this.currentEditorType === 'markdown') {
            const textarea = document.getElementById('markdown-content');
            if (textarea) textarea.value = content;
        } else {
            const editor = document.getElementById('rich-text-content');
            if (editor) editor.innerHTML = content;
        }
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
    
    setupToolbars() {
        this.setupMarkdownToolbar();
        this.setupRichTextToolbar();
    }
    
    setupMarkdownToolbar() {
        const toolbar = document.querySelector('#markdown-editor-container .editor-toolbar');
        if (!toolbar) return;
        
        toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('button[data-action]');
            if (!button) return;
            
            e.preventDefault();
            const action = button.dataset.action;
            this.executeMarkdownAction(action);
        });
    }
    
    setupRichTextToolbar() {
        const toolbar = document.getElementById('rich-text-toolbar');
        if (!toolbar) return;
        
        toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('button[data-command]');
            if (!button) return;
            
            e.preventDefault();
            const command = button.dataset.command;
            this.executeRichTextCommand(command);
        });
        
        toolbar.addEventListener('change', (e) => {
            const select = e.target.closest('select[data-command]');
            if (!select) return;
            
            const command = select.dataset.command;
            const value = select.value;
            this.executeRichTextCommand(command, value);
        });
    }
    
    executeMarkdownAction(action) {
        const textarea = document.getElementById('markdown-content');
        if (!textarea) return;
        
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const beforeText = textarea.value.substring(0, start);
        const afterText = textarea.value.substring(end);
        
        let replacement = '';
        let newCursorPos = start;
        
        switch (action) {
            case 'bold':
                replacement = `**${selectedText || 'texte en gras'}**`;
                newCursorPos = start + (selectedText ? replacement.length : 2);
                break;
            case 'italic':
                replacement = `*${selectedText || 'texte en italique'}*`;
                newCursorPos = start + (selectedText ? replacement.length : 1);
                break;
            case 'strikethrough':
                replacement = `~~${selectedText || 'texte barré'}~~`;
                newCursorPos = start + (selectedText ? replacement.length : 2);
                break;
            case 'heading':
                replacement = `## ${selectedText || 'Titre'}`;
                newCursorPos = start + replacement.length;
                break;
            case 'link':
                const url = prompt('URL du lien:');
                if (url) {
                    replacement = `[${selectedText || 'texte du lien'}](${url})`;
                    newCursorPos = start + replacement.length;
                }
                break;
            case 'image':
                const imageUrl = prompt('URL de l\\'image:');
                if (imageUrl) {
                    replacement = `![${selectedText || 'alt text'}](${imageUrl})`;
                    newCursorPos = start + replacement.length;
                }
                break;
            case 'list':
                replacement = `- ${selectedText || 'élément de liste'}`;
                newCursorPos = start + replacement.length;
                break;
            case 'ordered-list':
                replacement = `1. ${selectedText || 'élément de liste'}`;
                newCursorPos = start + replacement.length;
                break;
            case 'quote':
                replacement = `> ${selectedText || 'citation'}`;
                newCursorPos = start + replacement.length;
                break;
            case 'code':
                if (selectedText.includes('\\n')) {
                    replacement = `\\`\\`\\`\\n${selectedText}\\n\\`\\`\\``;
                } else {
                    replacement = `\\`${selectedText || 'code'}\\``;
                }
                newCursorPos = start + replacement.length;
                break;
        }
        
        if (replacement) {
            textarea.value = beforeText + replacement + afterText;
            textarea.setSelectionRange(newCursorPos, newCursorPos);
            textarea.focus();
            this.onContentChange();
            this.updatePreview();
        }
    }
    
    executeRichTextCommand(command, value = null) {
        const editor = document.getElementById('rich-text-content');
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
        } catch (error) {
            console.error('Rich text command error:', error);
        }
    }
    
    updatePreview() {
        if (this.currentEditorType !== 'markdown') return;
        
        const content = document.getElementById('markdown-content')?.value || '';
        const preview = document.getElementById('markdown-preview');
        
        if (preview) {
            preview.innerHTML = this.markdownToHtml(content);
        }
    }
    
    markdownToHtml(markdown) {
        if (typeof marked !== 'undefined') {
            return marked.parse(markdown);
        }
        
        // Simple markdown to HTML conversion
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\\*\\*(.*?)\\*\\*/gim, '<strong>$1</strong>')
            .replace(/\\*(.*?)\\*/gim, '<em>$1</em>')
            .replace(/~~(.*?)~~/gim, '<del>$1</del>')
            .replace(/\\`(.*?)\\`/gim, '<code>$1</code>')
            .replace(/\\n/gim, '<br>');
    }
    
    htmlToMarkdown(html) {
        // Simple HTML to markdown conversion
        return html
            .replace(/<h1>(.*?)<\\/h1>/gim, '# $1\\n')
            .replace(/<h2>(.*?)<\\/h2>/gim, '## $1\\n')
            .replace(/<h3>(.*?)<\\/h3>/gim, '### $1\\n')
            .replace(/<strong>(.*?)<\\/strong>/gim, '**$1**')
            .replace(/<em>(.*?)<\\/em>/gim, '*$1*')
            .replace(/<del>(.*?)<\\/del>/gim, '~~$1~~')
            .replace(/<code>(.*?)<\\/code>/gim, '`$1`')
            .replace(/<br\\s*\\/?>/gim, '\\n')
            .replace(/<[^>]+>/gim, ''); // Remove other HTML tags
    }
    
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
                this.showNotification('Erreur lors de l\\'enregistrement', 'error');
            }
            
            setTimeout(() => {
                indicator.textContent = '';
                indicator.className = 'auto-save-indicator';
            }, 3000);
        }
    }
    
    // Collaboration methods
    showAddCollaboratorModal() {
        const email = prompt('Email de l\\'utilisateur à ajouter:');
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
                this.showNotification(error.message || 'Erreur lors de l\\'ajout', 'error');
            }
        } catch (error) {
            console.error('Add collaborator error:', error);
            this.showNotification('Erreur lors de l\\'ajout du collaborateur', 'error');
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
        // Simple notification - can be enhanced with a proper notification system
        if (type === 'error') {
            alert('Erreur: ' + message);
        } else {
            console.log(message);
            // You can implement a toast notification here
        }
    }
}

// Additional utility functions
function insertImage() {
    const url = prompt('URL de l\\'image:');
    if (url) {
        document.execCommand('insertImage', false, url);
    }
}

// Initialize the document editor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.document-editor-container')) {
        new DocumentEditor();
    }
});

// Preview toggle for mobile
document.getElementById('toggle-preview')?.addEventListener('click', function() {
    const previewPane = document.querySelector('.preview-pane');
    previewPane.classList.toggle('show');
});