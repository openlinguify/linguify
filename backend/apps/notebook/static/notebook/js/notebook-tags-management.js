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
            '#8B5CF6'
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

        // Nouveau tag - Basculer vers l'onglet formulaire
        const createNewTagBtn = document.getElementById('createNewNotebookTagBtn');
        if (createNewTagBtn) {
            createNewTagBtn.addEventListener('click', () => this.showCreateTagForm());
        }
        
        // Bouton annuler dans le formulaire
        const cancelTagForm = document.getElementById('cancelTagForm');
        if (cancelTagForm) {
            cancelTagForm.addEventListener('click', () => this.cancelTagForm());
        }

        // Sélection de tous les tags
        const selectAllTags = document.getElementById('selectAllTags');
        if (selectAllTags) {
            selectAllTags.addEventListener('click', () => this.toggleSelectAll());
        }

        // Suppression des tags sélectionnés
        const deleteSelectedTagsBtn = document.getElementById('deleteSelectedTags');
        if (deleteSelectedTagsBtn) {
            deleteSelectedTagsBtn.addEventListener('click', () => this.deleteSelectedTags());
        }

        // Cancel selection
        const cancelSelection = document.getElementById('cancelSelection');
        if (cancelSelection) {
            cancelSelection.addEventListener('click', () => this.cancelSelection());
        }

        // Create tag buttons (including empty state)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('create-tag-btn')) {
                this.showCreateTagForm();
            }
        });

        // Sauvegarde du tag (création/édition)
        const saveTagBtn = document.getElementById('saveNotebookTagBtn');
        if (saveTagBtn) {
            saveTagBtn.addEventListener('click', () => this.saveTag());
        }

        // Aperçu couleur et couleurs prédéfinies
        const tagColorInput = document.getElementById('notebookTagColorInput');
        const tagNameInput = document.getElementById('notebookTagNameInput');
        if (tagColorInput && tagNameInput) {
            tagColorInput.addEventListener('input', () => this.updateTagPreview());
            tagNameInput.addEventListener('input', () => this.updateTagPreview());
        }

        // Couleurs prédéfinies
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('color-preset')) {
                const color = e.target.dataset.color;
                const colorInput = document.getElementById('notebookTagColorInput');
                if (colorInput) {
                    colorInput.value = color;
                    this.updateTagPreview();
                    this.updateColorPresets(color);
                }
            }
        });

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

    showCreateTagForm(tagData = null) {
        this.editingTag = tagData;
        
        const tagFormTab = document.getElementById('tag-form-tab');
        const tagFormTabText = document.getElementById('tagFormTabText');
        const saveTagBtnText = document.getElementById('saveTagBtnText');
        const tagNameInput = document.getElementById('notebookTagNameInput');
        const tagColorInput = document.getElementById('notebookTagColorInput');

        if (tagData) {
            tagFormTabText.textContent = 'Modifier étiquette';
            saveTagBtnText.textContent = 'Modifier';
            tagNameInput.value = tagData.name;
            tagColorInput.value = tagData.color || this.getRandomColor();
            this.updateColorPresets(tagData.color || this.getRandomColor());
        } else {
            tagFormTabText.textContent = 'Nouvelle étiquette';
            saveTagBtnText.textContent = 'Enregistrer';
            tagNameInput.value = '';
            const defaultColor = this.colors[0]; // Bleu par défaut
            tagColorInput.value = defaultColor;
            this.updateColorPresets(defaultColor);
        }

        this.updateTagPreview();
        
        // Basculer vers l'onglet formulaire
        const tabTrigger = new bootstrap.Tab(tagFormTab);
        tabTrigger.show();
        
        // Focus sur le nom
        setTimeout(() => tagNameInput.focus(), 300);
    }
    
    cancelTagForm() {
        // Reset du formulaire
        this.editingTag = null;
        const tagNameInput = document.getElementById('notebookTagNameInput');
        const tagColorInput = document.getElementById('notebookTagColorInput');
        
        if (tagNameInput) tagNameInput.value = '';
        if (tagColorInput) {
            const defaultColor = this.colors[0];
            tagColorInput.value = defaultColor;
            this.updateColorPresets(defaultColor);
        }
        
        this.updateTagPreview();
        
        // Retourner à l'onglet liste
        const tagsListTab = document.getElementById('tags-list-tab');
        const tabTrigger = new bootstrap.Tab(tagsListTab);
        tabTrigger.show();
    }

    updateTagPreview() {
        const tagNameInput = document.getElementById('notebookTagNameInput');
        const tagColorInput = document.getElementById('notebookTagColorInput');
        const previewText = document.getElementById('previewText');
        const tagPreview = document.getElementById('notebookTagPreview');

        if (tagNameInput && tagColorInput && previewText && tagPreview) {
            const name = tagNameInput.value || 'Apercu';
            const color = tagColorInput.value;
            
            previewText.textContent = name;
            const badge = tagPreview.querySelector('.badge');
            if (badge) {
                badge.style.background = color;
            }
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
        const tagsGrid = document.getElementById('tagsGrid');
        const tagsEmptyState = document.getElementById('tagsEmptyState');
        if (!tagsGrid) return;

        // Filtrer les tags selon la recherche
        let filteredTags = this.tags;
        if (this.searchQuery) {
            filteredTags = this.tags.filter(tag => 
                tag.name.toLowerCase().includes(this.searchQuery)
            );
        }

        // Afficher empty state si aucun tag
        if (filteredTags.length === 0) {
            tagsGrid.style.display = 'none';
            if (tagsEmptyState) {
                tagsEmptyState.style.display = 'block';
            }
            return;
        } else {
            tagsGrid.style.display = 'block';
            if (tagsEmptyState) {
                tagsEmptyState.style.display = 'none';
            }
        }

        tagsGrid.innerHTML = filteredTags.map(tag => `
            <div class="col-md-6 col-xl-4 tag-card-item">
                <div class="card h-100 border-0 shadow-sm tag-card ${this.selectedTags.has(tag.id) ? 'selected-tag' : ''}" style="transition: all 0.3s ease; border-radius: 1rem;">
                    <div class="card-body p-3">
                        <div class="d-flex align-items-center justify-content-between mb-3">
                            <div class="d-flex align-items-center">
                                <input type="checkbox" class="form-check-input me-2 tag-checkbox" 
                                       data-tag-id="${tag.id}" ${this.selectedTags.has(tag.id) ? 'checked' : ''}
                                       style="${this.selectedTags.size > 0 ? 'display: block' : 'display: none'}">
                                <div class="tag-color-preview rounded-circle me-2" style="width: 12px; height: 12px; background: ${tag.color};"></div>
                                <h6 class="mb-0 fw-bold tag-name" style="color: var(--linguify-gray-800);">${tag.name}</h6>
                            </div>
                            <div class="dropdown">
                                <button class="btn btn-link btn-sm p-1 text-muted" data-bs-toggle="dropdown">
                                    <i class="bi bi-three-dots-vertical"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                                    <li><a class="dropdown-item edit-tag" href="#" data-tag-id="${tag.id}"><i class="bi bi-pencil me-2"></i>Modifier</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item text-danger delete-tag" href="#" data-tag-id="${tag.id}"><i class="bi bi-trash2 me-2"></i>Supprimer</a></li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-between">
                            <span class="badge rounded-pill px-3 py-2" style="background: rgba(${this.hexToRgb(tag.color)}, 0.1); color: ${tag.color}; font-weight: 500;">
                                <i class="bi bi-journal-text me-1" style="font-size: 0.75rem;"></i>
                                ${tag.usage_count} note${tag.usage_count > 1 ? 's' : ''}
                            </span>
                            <small class="text-muted">Cree recemment</small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        // Event listeners pour les actions
        this.attachTagCardEventListeners();
        this.updateSelectionInterface();
    }

    attachTagCardEventListeners() {
        const tagsGrid = document.getElementById('tagsGrid');
        if (!tagsGrid) return;

        // Event listeners pour les checkboxes
        tagsGrid.querySelectorAll('.tag-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const tagId = parseInt(e.target.dataset.tagId);
                if (e.target.checked) {
                    this.selectedTags.add(tagId);
                } else {
                    this.selectedTags.delete(tagId);
                }
                this.updateSelectionInterface();
                this.renderTags(); // Re-render to update selected state
            });
        });

        // Event listeners pour les actions edit/delete
        tagsGrid.querySelectorAll('.edit-tag').forEach(editBtn => {
            editBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const tagId = parseInt(e.target.closest('.edit-tag').dataset.tagId);
                this.editTag(tagId);
            });
        });

        tagsGrid.querySelectorAll('.delete-tag').forEach(deleteBtn => {
            deleteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const tagId = parseInt(e.target.closest('.delete-tag').dataset.tagId);
                this.deleteTag(tagId);
            });
        });
    }

    updateTagsCount() {
        const tagsCount = document.getElementById('notebookTagsCount');
        if (tagsCount) {
            const count = this.tags.length;
            tagsCount.textContent = count;
            
            // Mettre à jour le texte suivant pour le pluriel
            const parentSpan = tagsCount.parentElement;
            if (parentSpan && parentSpan.querySelector('.text-muted')) {
                const textAfterCount = count <= 1 ? 'étiquette' : 'étiquettes';
                parentSpan.innerHTML = `<span id="notebookTagsCount">${count}</span> ${textAfterCount}`;
            }
        }
    }
    
    updateColorPresets(selectedColor) {
        // Mettre à jour l'état sélectionné des couleurs prédéfinies
        document.querySelectorAll('.color-preset').forEach(preset => {
            if (preset.dataset.color === selectedColor) {
                preset.classList.add('selected');
            } else {
                preset.classList.remove('selected');
            }
        });
    }
    
    hexToRgb(hex) {
        // Convertir hex en RGB pour les couleurs avec transparence
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? 
            `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : 
            '59, 130, 246'; // Fallback bleu Linguify
    }

    updateSelectionInterface() {
        const selectionMode = document.getElementById('selectionMode');
        const selectedTagsCount = document.getElementById('selectedTagsCount');
        const tagsGrid = document.getElementById('tagsGrid');
        
        if (this.selectedTags.size > 0) {
            // Afficher le mode sélection
            if (selectionMode) {
                selectionMode.classList.remove('d-none');
            }
            if (selectedTagsCount) {
                selectedTagsCount.textContent = `${this.selectedTags.size} selectionnee${this.selectedTags.size > 1 ? 's' : ''}`;
            }
            // Afficher les checkboxes
            if (tagsGrid) {
                tagsGrid.querySelectorAll('.tag-checkbox').forEach(cb => {
                    cb.style.display = 'block';
                });
                tagsGrid.classList.add('selection-mode');
            }
        } else {
            // Cacher le mode sélection
            if (selectionMode) {
                selectionMode.classList.add('d-none');
            }
            // Cacher les checkboxes
            if (tagsGrid) {
                tagsGrid.querySelectorAll('.tag-checkbox').forEach(cb => {
                    cb.style.display = 'none';
                });
                tagsGrid.classList.remove('selection-mode');
            }
        }
    }

    toggleSelectAll() {
        // Filtrer les tags selon la recherche actuelle
        let filteredTags = this.tags;
        if (this.searchQuery) {
            filteredTags = this.tags.filter(tag => 
                tag.name.toLowerCase().includes(this.searchQuery)
            );
        }
        
        // Si tous les tags filtrés sont sélectionnés, tout déselectionner
        const allSelected = filteredTags.every(tag => this.selectedTags.has(tag.id));
        
        if (allSelected) {
            // Désélectionner tous les tags filtrés
            filteredTags.forEach(tag => this.selectedTags.delete(tag.id));
        } else {
            // Sélectionner tous les tags filtrés
            filteredTags.forEach(tag => this.selectedTags.add(tag.id));
        }

        this.renderTags();
    }
    
    cancelSelection() {
        this.selectedTags.clear();
        this.renderTags();
    }

    editTag(tagId) {
        const tag = this.tags.find(t => t.id === tagId);
        if (tag) {
            this.showCreateTagForm(tag);
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

            // Retourner à l'onglet liste
            const tagsListTab = document.getElementById('tags-list-tab');
            const tabTrigger = new bootstrap.Tab(tagsListTab);
            tabTrigger.show();
            
            // Reset du formulaire
            this.cancelTagForm();

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