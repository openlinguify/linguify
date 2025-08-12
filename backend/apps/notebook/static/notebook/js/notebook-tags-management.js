// Gestion des tags pour le Notebook - Interface style OpenLinguify
class NotebookTagsManagement {
    constructor() {
        this.tags = [];
        this.selectedTags = new Set();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.searchQuery = '';
        this.editingTag = null;
        this.colors = [
            '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
            '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16',
            '#F97316', '#6366F1', '#14B8A6', '#F43F5E',
            '#22C55E', '#A855F7', '#3B82F6', '#EF4444'
        ];
    }

    init() {
        this.setupEventListeners();
        this.initializeTagsInput();
    }

    setupEventListeners() {
        // Bouton principal pour ouvrir la gestion des tags
        const manageTagsBtn = document.getElementById('manageNotebookTagsBtn');
        if (manageTagsBtn) {
            manageTagsBtn.addEventListener('click', () => this.showTagsManagement());
        }

        // Recherche
        const searchInput = document.getElementById('notebookTagsSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.renderTags();
            });
        }

        // Nouveau tag
        const createNewTagBtn = document.getElementById('createNewNotebookTagBtn');
        if (createNewTagBtn) {
            createNewTagBtn.addEventListener('click', () => this.showCreateTagModal());
        }

        // Sélection de tous les tags
        const selectAllTags = document.getElementById('selectAllNotebookTags');
        if (selectAllTags) {
            selectAllTags.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
        }

        // Suppression des tags sélectionnés
        const deleteSelectedTagsBtn = document.getElementById('deleteSelectedNotebookTagsBtn');
        if (deleteSelectedTagsBtn) {
            deleteSelectedTagsBtn.addEventListener('click', () => this.deleteSelectedTags());
        }

        // Sauvegarde du tag (création/édition)
        const saveTagBtn = document.getElementById('saveNotebookTagBtn');
        if (saveTagBtn) {
            saveTagBtn.addEventListener('click', () => this.saveTag());
        }

        // Aperçu couleur
        const tagColorInput = document.getElementById('notebookTagColorInput');
        const tagNameInput = document.getElementById('notebookTagNameInput');
        if (tagColorInput && tagNameInput) {
            tagColorInput.addEventListener('input', () => this.updateTagPreview());
            tagNameInput.addEventListener('input', () => this.updateTagPreview());
        }

        // Validation du formulaire
        const tagEditForm = document.getElementById('notebookTagEditForm');
        if (tagEditForm) {
            tagEditForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveTag();
            });
        }
    }

    initializeTagsInput() {
        // Initialiser le système de tags pour les notes
        const noteTagsInput = document.getElementById('noteTagsInput');
        if (noteTagsInput) {
            noteTagsInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.addTagToNote(e.target.value.trim());
                }
            });
        }
    }

    async showTagsManagement() {
        await this.loadTags();
        const modal = new bootstrap.Modal(document.getElementById('notebookTagsManagementModal'));
        modal.show();
    }

    showCreateTagModal(tagData = null) {
        this.editingTag = tagData;
        
        const modal = new bootstrap.Modal(document.getElementById('notebookTagEditModal'));
        const modalTitle = document.getElementById('notebookTagEditModalLabel');
        const tagNameInput = document.getElementById('notebookTagNameInput');
        const tagColorInput = document.getElementById('notebookTagColorInput');

        if (tagData) {
            modalTitle.textContent = 'Modifier l\'étiquette';
            tagNameInput.value = tagData.name;
            tagColorInput.value = tagData.color || this.getRandomColor();
        } else {
            modalTitle.textContent = 'Nouvelle étiquette';
            tagNameInput.value = '';
            tagColorInput.value = this.getRandomColor();
        }

        this.updateTagPreview();
        modal.show();
        
        // Focus sur le nom
        setTimeout(() => tagNameInput.focus(), 300);
    }

    updateTagPreview() {
        const tagNameInput = document.getElementById('notebookTagNameInput');
        const tagColorInput = document.getElementById('notebookTagColorInput');
        const tagPreview = document.getElementById('notebookTagPreview');

        if (tagNameInput && tagColorInput && tagPreview) {
            const name = tagNameInput.value || 'Aperçu';
            const color = tagColorInput.value;
            
            tagPreview.innerHTML = `<span class="badge" style="background: ${color}; color: white;">${name}</span>`;
        }
    }

    getRandomColor() {
        return this.colors[Math.floor(Math.random() * this.colors.length)];
    }

    async loadTags() {
        try {
            // Pour l'instant, on simule la récupération des tags depuis l'API notebook
            // Plus tard, on connectera à l'API réelle du notebook
            this.tags = [
                { id: 1, name: 'Vocabulaire', color: '#3B82F6', usage_count: 15 },
                { id: 2, name: 'Grammaire', color: '#EF4444', usage_count: 8 },
                { id: 3, name: 'Expressions', color: '#10B981', usage_count: 12 },
                { id: 4, name: 'Culture', color: '#F59E0B', usage_count: 5 },
                { id: 5, name: 'Important', color: '#EC4899', usage_count: 20 },
                { id: 6, name: 'À réviser', color: '#8B5CF6', usage_count: 7 },
            ];

            this.renderTags();
            this.updateTagsCount();

        } catch (error) {
            console.error('Erreur lors du chargement des tags:', error);
            this.showNotification('Erreur lors du chargement des étiquettes', 'error');
        }
    }

    renderTags() {
        const tbody = document.getElementById('notebookTagsTableBody');
        if (!tbody) return;

        // Filtrer les tags selon la recherche
        let filteredTags = this.tags;
        if (this.searchQuery) {
            filteredTags = this.tags.filter(tag => 
                tag.name.toLowerCase().includes(this.searchQuery)
            );
        }

        // Pagination
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedTags = filteredTags.slice(startIndex, endIndex);

        tbody.innerHTML = paginatedTags.map(tag => `
            <tr>
                <td>
                    <input type="checkbox" class="form-check-input tag-checkbox" 
                           data-tag-id="${tag.id}" ${this.selectedTags.has(tag.id) ? 'checked' : ''}>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <span class="badge me-2" style="background: ${tag.color}; color: white;">${tag.name}</span>
                    </div>
                </td>
                <td>
                    <div class="color-display" style="width: 20px; height: 20px; background: ${tag.color}; border-radius: 3px; border: 1px solid #ddd;"></div>
                </td>
                <td>
                    <span class="text-muted">${tag.usage_count}</span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="window.notebookTagsManagement.editTag(${tag.id})" title="Modifier">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="window.notebookTagsManagement.deleteTag(${tag.id})" title="Supprimer">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        // Event listeners pour les checkboxes
        tbody.querySelectorAll('.tag-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const tagId = parseInt(e.target.dataset.tagId);
                if (e.target.checked) {
                    this.selectedTags.add(tagId);
                } else {
                    this.selectedTags.delete(tagId);
                }
                this.updateDeleteButton();
            });
        });

        this.renderPagination(filteredTags.length);
    }

    renderPagination(totalItems) {
        const pagination = document.getElementById('notebookTagsPagination');
        if (!pagination) return;

        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = '';
        
        // Bouton précédent
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.notebookTagsManagement.goToPage(${this.currentPage - 1})">Précédent</a>
            </li>
        `;

        // Numéros de pages
        for (let i = 1; i <= totalPages; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="window.notebookTagsManagement.goToPage(${i})">${i}</a>
                </li>
            `;
        }

        // Bouton suivant
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.notebookTagsManagement.goToPage(${this.currentPage + 1})">Suivant</a>
            </li>
        `;

        pagination.innerHTML = paginationHTML;
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.tags.length / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderTags();
        }
    }

    updateTagsCount() {
        const tagsCount = document.getElementById('notebookTagsCount');
        if (tagsCount) {
            tagsCount.textContent = `${this.tags.length} étiquette(s)`;
        }
    }

    updateDeleteButton() {
        const deleteBtn = document.getElementById('deleteSelectedNotebookTagsBtn');
        if (deleteBtn) {
            if (this.selectedTags.size > 0) {
                deleteBtn.style.display = 'inline-block';
                deleteBtn.innerHTML = `<i class="bi bi-trash me-1"></i>Supprimer (${this.selectedTags.size})`;
            } else {
                deleteBtn.style.display = 'none';
            }
        }
    }

    toggleSelectAll(checked) {
        this.selectedTags.clear();
        
        if (checked) {
            // Filtrer les tags selon la recherche actuelle
            let filteredTags = this.tags;
            if (this.searchQuery) {
                filteredTags = this.tags.filter(tag => 
                    tag.name.toLowerCase().includes(this.searchQuery)
                );
            }
            
            // Pagination
            const startIndex = (this.currentPage - 1) * this.itemsPerPage;
            const endIndex = startIndex + this.itemsPerPage;
            const paginatedTags = filteredTags.slice(startIndex, endIndex);
            
            paginatedTags.forEach(tag => this.selectedTags.add(tag.id));
        }

        this.renderTags();
        this.updateDeleteButton();
    }

    editTag(tagId) {
        const tag = this.tags.find(t => t.id === tagId);
        if (tag) {
            this.showCreateTagModal(tag);
        }
    }

    async deleteTag(tagId) {
        const tag = this.tags.find(t => t.id === tagId);
        if (!tag) return;

        if (!confirm(`Êtes-vous sûr de vouloir supprimer l'étiquette "${tag.name}" ?`)) {
            return;
        }

        try {
            // Pour l'instant, on simule la suppression
            this.tags = this.tags.filter(t => t.id !== tagId);
            this.selectedTags.delete(tagId);
            
            this.renderTags();
            this.updateTagsCount();
            this.updateDeleteButton();
            
            this.showNotification(`Étiquette "${tag.name}" supprimée`, 'success');

        } catch (error) {
            console.error('Erreur lors de la suppression du tag:', error);
            this.showNotification('Erreur lors de la suppression de l\'étiquette', 'error');
        }
    }

    async deleteSelectedTags() {
        if (this.selectedTags.size === 0) return;

        if (!confirm(`Êtes-vous sûr de vouloir supprimer ${this.selectedTags.size} étiquette(s) ?`)) {
            return;
        }

        try {
            // Pour l'instant, on simule la suppression
            const tagsToDelete = Array.from(this.selectedTags);
            this.tags = this.tags.filter(tag => !this.selectedTags.has(tag.id));
            this.selectedTags.clear();
            
            this.renderTags();
            this.updateTagsCount();
            this.updateDeleteButton();
            
            this.showNotification(`${tagsToDelete.length} étiquette(s) supprimée(s)`, 'success');

        } catch (error) {
            console.error('Erreur lors de la suppression des tags:', error);
            this.showNotification('Erreur lors de la suppression des étiquettes', 'error');
        }
    }

    async saveTag() {
        const tagNameInput = document.getElementById('notebookTagNameInput');
        const tagColorInput = document.getElementById('notebookTagColorInput');

        if (!tagNameInput || !tagColorInput) return;

        const tagName = tagNameInput.value.trim();
        const tagColor = tagColorInput.value;

        if (!tagName) {
            this.showNotification('Le nom de l\'étiquette est requis', 'error');
            return;
        }

        try {
            if (this.editingTag) {
                // Modification
                const tagIndex = this.tags.findIndex(t => t.id === this.editingTag.id);
                if (tagIndex !== -1) {
                    this.tags[tagIndex] = {
                        ...this.tags[tagIndex],
                        name: tagName,
                        color: tagColor
                    };
                }
                this.showNotification('Étiquette modifiée avec succès', 'success');
            } else {
                // Création
                const newTag = {
                    id: Math.max(...this.tags.map(t => t.id), 0) + 1,
                    name: tagName,
                    color: tagColor,
                    usage_count: 0
                };
                this.tags.push(newTag);
                this.showNotification('Étiquette créée avec succès', 'success');
            }

            // Fermer la modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('notebookTagEditModal'));
            modal.hide();

            // Recharger la liste
            this.renderTags();
            this.updateTagsCount();

        } catch (error) {
            console.error('Erreur lors de la sauvegarde du tag:', error);
            this.showNotification('Erreur lors de la sauvegarde de l\'étiquette', 'error');
        }
    }

    async addTagToNote(tagName) {
        if (!tagName) return;

        // Vérifier si le tag existe déjà
        const existingTag = this.tags.find(t => t.name.toLowerCase() === tagName.toLowerCase());
        
        if (!existingTag) {
            // Créer le tag s'il n'existe pas
            const newTag = {
                id: Math.max(...this.tags.map(t => t.id), 0) + 1,
                name: tagName,
                color: this.getRandomColor(),
                usage_count: 1
            };
            this.tags.push(newTag);
        }

        // Ajouter le tag à l'affichage de la note
        this.displayNoteTag(tagName, existingTag?.color || this.getRandomColor());

        // Effacer l'input
        const noteTagsInput = document.getElementById('noteTagsInput');
        if (noteTagsInput) {
            noteTagsInput.value = '';
        }
    }

    displayNoteTag(tagName, color) {
        const noteTagsDisplay = document.getElementById('noteTagsDisplay');
        if (!noteTagsDisplay) return;

        // Vérifier si le tag n'est pas déjà affiché
        const existingTags = Array.from(noteTagsDisplay.querySelectorAll('.tag-item span'));
        if (existingTags.some(tag => tag.textContent === tagName)) {
            return;
        }

        const tagElement = document.createElement('div');
        tagElement.className = 'tag-item';
        tagElement.innerHTML = `
            <span class="badge" style="background: ${color}; color: white;">${tagName}</span>
            <button type="button" class="tag-remove" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;

        noteTagsDisplay.appendChild(tagElement);
    }

    showNotification(message, type = 'info') {
        // Système de notification simple
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove après 5 secondes
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Instancier la classe globalement
window.notebookTagsManagement = new NotebookTagsManagement();

// Initialiser au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    window.notebookTagsManagement.init();
});