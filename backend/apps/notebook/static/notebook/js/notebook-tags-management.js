// Gestion des tags pour le Notebook - Interface style OpenLinguify
class NotebookTagsManagement {
    constructor() {
        this.tags = [];
        this.selectedTags = new Set();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.searchQuery = '';
        this.editingTag = null;
        this.inlineEditingTag = null;
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

        // Checkbox "Sélectionner tout" dans l'en-tête du tableau
        const selectAllTagsCheckbox = document.getElementById('selectAllTagsCheckbox');
        if (selectAllTagsCheckbox) {
            selectAllTagsCheckbox.addEventListener('change', () => this.toggleSelectAll());
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

        // Inline edit events
        const cancelInlineEdit = document.getElementById('cancelInlineEdit');
        if (cancelInlineEdit) {
            cancelInlineEdit.addEventListener('click', () => this.cancelInlineEdit());
        }

        const saveInlineEdit = document.getElementById('saveInlineEdit');
        if (saveInlineEdit) {
            saveInlineEdit.addEventListener('click', () => this.saveInlineEdit());
        }

        // Inline preview update
        const inlineTagNameInput = document.getElementById('inlineTagNameInput');
        const inlineTagColorInput = document.getElementById('inlineTagColorInput');
        if (inlineTagNameInput && inlineTagColorInput) {
            inlineTagNameInput.addEventListener('input', () => this.updateInlineTagPreview());
            inlineTagColorInput.addEventListener('input', () => this.updateInlineTagPreview());
        }

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
            console.log('🔄 Chargement des tags depuis l\'API globale...');
            
            const csrfToken = this.getCSRFToken();
            console.log('🔐 CSRF Token:', csrfToken ? 'Found' : 'Not found');
            
            // Appeler l'API du système de tags global
            const response = await fetch('/api/v1/core/tags/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'  // Inclure les cookies de session
            });
            
            console.log('📡 Response status:', response.status);
            console.log('📡 Response headers:', response.headers);

            if (response.ok) {
                const data = await response.json();
                console.log('✅ API Data:', data);
                console.log('✅ Data type:', typeof data);
                console.log('✅ Data keys:', Object.keys(data));
                
                // Gérer différents formats de réponse API
                let tagsArray = [];
                
                if (data && Array.isArray(data.results)) {
                    // Format pagination DRF: {results: [...], count: N}
                    tagsArray = data.results;
                    console.log('✅ Format DRF pagination détecté');
                } else if (data && Array.isArray(data)) {
                    // Format liste directe: [...]
                    tagsArray = data;
                    console.log('✅ Format liste directe détecté');
                } else if (data && typeof data === 'object' && !Array.isArray(data)) {
                    // Format objet avec propriétés inconnues - chercher une liste
                    const possibleArrays = Object.values(data).filter(v => Array.isArray(v));
                    if (possibleArrays.length > 0) {
                        tagsArray = possibleArrays[0];
                        console.log('✅ Format objet avec liste trouvé');
                    }
                } else {
                    console.log('❌ Format de données non reconnu, utilisation d\'un tableau vide');
                    tagsArray = [];
                }
                
                console.log('✅ Tags array:', tagsArray);
                console.log('✅ Tags array length:', tagsArray.length);
                
                // Vérifier que chaque élément a les propriétés nécessaires
                if (tagsArray.length > 0) {
                    console.log('✅ Premier tag:', tagsArray[0]);
                }
                
                // Transformer les données de l'API pour correspondre au format attendu
                this.tags = tagsArray.map(tag => ({
                    id: tag.id || tag.pk || Math.random().toString(),
                    name: tag.name || tag.display_name || 'Tag sans nom',
                    color: tag.color || '#3B82F6',
                    description: tag.description || '',
                    usage_count: tag.usage_count_notebook || tag.usage_count || 0,
                    usage_count_total: tag.usage_count_total || tag.total_usage || 0,
                    is_favorite: tag.is_favorite || false,
                    created_at: tag.created_at || new Date().toISOString()
                }));

                console.log(`✅ Tags chargés: ${this.tags.length} tags trouvés`);
            } else {
                console.error('❌ Erreur API:', response.status, response.statusText);
                const errorText = await response.text();
                console.error('❌ Réponse détaillée:', errorText);
                // Fallback avec les tags mockés si l'API échoue
                this.tags = [
                    { id: 'fallback-1', name: 'API non accessible', color: '#6B7280', usage_count: 0 }
                ];
            }

            this.renderTags();
            this.updateTagsCount();

        } catch (error) {
            console.error('❌ Erreur lors du chargement des tags:', error);
            
            // Fallback avec les tags mockés en cas d'erreur
            this.tags = [
                { id: 'error-1', name: 'Erreur de connexion', color: '#EF4444', usage_count: 0 }
            ];
            
            this.renderTags();
            this.updateTagsCount();
            this.showNotification('Impossible de charger les étiquettes', 'error');
        }
    }

    // === NOUVELLES FONCTIONS POUR L'INTÉGRATION API ===
    
    // Obtenir l'ID de la note actuellement sélectionnée
    getCurrentNoteId() {
        // Chercher la note active dans le sidebar ou l'éditeur
        const activeNote = document.querySelector('.notebook-note-item.active');
        if (activeNote) {
            return activeNote.dataset.noteId;
        }
        
        // Fallback: chercher dans l'éditeur
        const editorTitleInput = document.getElementById('note-title');
        if (editorTitleInput && editorTitleInput.dataset.noteId) {
            return editorTitleInput.dataset.noteId;
        }
        
        return null;
    }

    // Récupérer les tags d'une note spécifique
    async getNoteTags(noteId) {
        if (!noteId) return [];
        
        try {
            console.log('🔄 Récupération des tags pour la note:', noteId);
            
            const response = await fetch(`/api/v1/core/object-tags/get_object_tags/?app_name=notebook&model_name=Note&object_id=${noteId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const tags = await response.json();
                console.log('✅ Tags de la note récupérés:', tags);
                return tags;
            } else {
                console.error('❌ Erreur récupération tags note:', response.status);
                return [];
            }
        } catch (error) {
            console.error('❌ Erreur lors de la récupération des tags de la note:', error);
            return [];
        }
    }

    // Appliquer des tags à une note
    async setNoteTags(noteId, tagIds) {
        if (!noteId) {
            console.error('❌ Note ID requis pour appliquer des tags');
            return false;
        }

        try {
            console.log('🔄 Application des tags à la note:', noteId, tagIds);
            
            const response = await fetch('/api/v1/core/object-tags/set_object_tags/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    app_name: 'notebook',
                    model_name: 'Note',
                    object_id: noteId,
                    tag_ids: tagIds
                })
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Tags appliqués avec succès:', result);
                
                // Recharger les tags pour mettre à jour les compteurs
                await this.loadTags();
                this.renderTags();
                
                return true;
            } else {
                console.error('❌ Erreur application tags:', response.status);
                const errorText = await response.text();
                console.error('❌ Détails:', errorText);
                return false;
            }
        } catch (error) {
            console.error('❌ Erreur lors de l\'application des tags:', error);
            return false;
        }
    }

    // Méthode utilitaire pour obtenir le token CSRF - compatible avec le système Linguify
    getCSRFToken() {
        // Utiliser la fonction globale définie dans le template base si disponible
        if (window.NotebookAPI && window.NotebookAPI.getCSRFToken) {
            return window.NotebookAPI.getCSRFToken();
        }
        
        // Fallback: chercher dans plusieurs sources
        var tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        var metaElement = document.querySelector('meta[name=csrf-token]');
        var cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
            
        return (tokenElement && tokenElement.value) || 
               (metaElement && metaElement.getAttribute('content')) || 
               window.csrfToken || 
               cookieValue || '';
    }

    renderTags() {
        const tagsTableBody = document.getElementById('tagsTableBody');
        const tagsTable = document.getElementById('tagsTable');
        const tagsEmptyState = document.getElementById('tagsEmptyState');
        if (!tagsTableBody) return;

        // Filtrer les tags selon la recherche
        let filteredTags = this.tags;
        if (this.searchQuery) {
            filteredTags = this.tags.filter(tag => 
                tag.name.toLowerCase().includes(this.searchQuery)
            );
        }

        // Afficher empty state si aucun tag
        if (filteredTags.length === 0) {
            if (tagsTable) tagsTable.style.display = 'none';
            if (tagsEmptyState) {
                tagsEmptyState.style.display = 'block';
            }
            return;
        } else {
            if (tagsTable) tagsTable.style.display = 'table';
            if (tagsEmptyState) {
                tagsEmptyState.style.display = 'none';
            }
        }

        tagsTableBody.innerHTML = filteredTags.map(tag => `
            <tr class="${this.selectedTags.has(tag.id) ? 'selected' : ''}" data-tag-id="${tag.id}">
                <td class="tag-checkbox-cell">
                    <input type="checkbox" class="form-check-input tag-checkbox" 
                           data-tag-id="${tag.id}" ${this.selectedTags.has(tag.id) ? 'checked' : ''}
                           style="${this.selectedTags.size > 0 ? 'display: block' : 'display: none'}">
                </td>
                <td>
                    <div class="tag-color-dot" style="background: ${tag.color};"></div>
                </td>
                <td class="tag-name-cell">${tag.name}</td>
                <td>
                    <span class="tag-usage-badge">
                        <i class="bi bi-journal-text"></i>
                        ${tag.usage_count} note${tag.usage_count !== 1 ? 's' : ''}
                    </span>
                </td>
                <td>
                    <span class="tag-date-text">Créé récemment</span>
                </td>
                <td>
                    <div class="tag-actions">
                        <button type="button" class="tag-action-btn edit-tag" data-tag-id="${tag.id}" title="Modifier">
                            <i class="bi bi-pencil" style="font-size: 0.75rem;"></i>
                        </button>
                        <button type="button" class="tag-action-btn delete delete-tag" data-tag-id="${tag.id}" title="Supprimer">
                            <i class="bi bi-trash2" style="font-size: 0.75rem;"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        // Event listeners pour les actions
        this.attachTagTableEventListeners();
        this.updateSelectionInterface();
    }

    attachTagTableEventListeners() {
        const tagsTableBody = document.getElementById('tagsTableBody');
        if (!tagsTableBody) return;

        // Event listeners pour les checkboxes
        tagsTableBody.querySelectorAll('.tag-checkbox').forEach(checkbox => {
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
        tagsTableBody.querySelectorAll('.edit-tag').forEach(editBtn => {
            editBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const tagId = parseInt(e.target.dataset.tagId);
                this.editTag(tagId);
            });
        });

        tagsTableBody.querySelectorAll('.delete-tag').forEach(deleteBtn => {
            deleteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const tagId = parseInt(e.target.dataset.tagId);
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
        const tagsTable = document.getElementById('tagsTable');
        const selectAllCheckbox = document.getElementById('selectAllTagsCheckbox');
        
        if (this.selectedTags.size > 0) {
            // Afficher le mode sélection
            if (selectionMode) {
                selectionMode.classList.remove('d-none');
            }
            if (selectedTagsCount) {
                selectedTagsCount.textContent = `${this.selectedTags.size} selectionnee${this.selectedTags.size > 1 ? 's' : ''}`;
            }
            // Afficher les checkboxes
            if (tagsTable) {
                tagsTable.classList.add('selection-mode');
                // Afficher la checkbox "Sélectionner tout"
                if (selectAllCheckbox) {
                    selectAllCheckbox.style.display = 'block';
                }
            }
        } else {
            // Cacher le mode sélection
            if (selectionMode) {
                selectionMode.classList.add('d-none');
            }
            // Cacher les checkboxes
            if (tagsTable) {
                tagsTable.classList.remove('selection-mode');
                // Cacher la checkbox "Sélectionner tout"
                if (selectAllCheckbox) {
                    selectAllCheckbox.style.display = 'none';
                }
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
            this.showInlineEditForm(tag);
        }
    }

    showInlineEditForm(tag) {
        this.inlineEditingTag = tag;
        
        // Remplir le formulaire
        const inlineTagNameInput = document.getElementById('inlineTagNameInput');
        const inlineTagColorInput = document.getElementById('inlineTagColorInput');
        
        if (inlineTagNameInput && inlineTagColorInput) {
            inlineTagNameInput.value = tag.name;
            inlineTagColorInput.value = tag.color;
            this.updateInlineTagPreview();
        }
        
        // Afficher le formulaire inline
        const inlineEditForm = document.getElementById('inlineEditForm');
        if (inlineEditForm) {
            inlineEditForm.style.display = 'block';
            // Scroll vers le formulaire
            inlineEditForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            // Focus sur le nom
            setTimeout(() => inlineTagNameInput?.focus(), 300);
        }
    }

    cancelInlineEdit() {
        this.inlineEditingTag = null;
        
        // Cacher le formulaire
        const inlineEditForm = document.getElementById('inlineEditForm');
        if (inlineEditForm) {
            inlineEditForm.style.display = 'none';
        }
        
        // Reset des champs
        const inlineTagNameInput = document.getElementById('inlineTagNameInput');
        const inlineTagColorInput = document.getElementById('inlineTagColorInput');
        if (inlineTagNameInput) inlineTagNameInput.value = '';
        if (inlineTagColorInput) inlineTagColorInput.value = '#3B82F6';
        this.updateInlineTagPreview();
    }

    async saveInlineEdit() {
        if (!this.inlineEditingTag) return;

        const inlineTagNameInput = document.getElementById('inlineTagNameInput');
        const inlineTagColorInput = document.getElementById('inlineTagColorInput');

        if (!inlineTagNameInput || !inlineTagColorInput) return;

        const tagName = inlineTagNameInput.value.trim();
        const tagColor = inlineTagColorInput.value;

        if (!tagName) {
            this.showNotification('Le nom de l\'étiquette est requis', 'error');
            return;
        }

        try {
            const csrfToken = this.getCSRFToken();
            
            console.log('🔄 Modification inline du tag:', this.inlineEditingTag.id);
            
            const response = await fetch(`/api/v1/core/tags/${this.inlineEditingTag.id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    name: tagName,
                    color: tagColor
                })
            });

            if (response.ok) {
                const updatedTag = await response.json();
                console.log('✅ Tag modifié (inline):', updatedTag);
                
                // Mettre à jour dans la liste locale
                const tagIndex = this.tags.findIndex(t => t.id === this.inlineEditingTag.id);
                if (tagIndex !== -1) {
                    this.tags[tagIndex] = {
                        ...this.tags[tagIndex],
                        name: updatedTag.name || updatedTag.display_name,
                        color: updatedTag.color
                    };
                }
                
                // Cacher le formulaire et re-render
                this.cancelInlineEdit();
                this.renderTags();
                this.showNotification('Étiquette modifiée avec succès', 'success');
            } else {
                console.error('❌ Erreur modification inline:', response.status);
                const errorText = await response.text();
                console.error('❌ Détails:', errorText);
                this.showNotification('Erreur lors de la modification', 'error');
            }
        } catch (error) {
            console.error('❌ Erreur lors de la modification inline:', error);
            this.showNotification('Erreur lors de la modification', 'error');
        }
    }

    updateInlineTagPreview() {
        const inlineTagNameInput = document.getElementById('inlineTagNameInput');
        const inlineTagColorInput = document.getElementById('inlineTagColorInput');
        const inlinePreviewText = document.getElementById('inlinePreviewText');
        const inlineTagPreview = document.getElementById('inlineTagPreview');

        if (inlineTagNameInput && inlineTagColorInput && inlinePreviewText && inlineTagPreview) {
            const name = inlineTagNameInput.value || 'Aperçu';
            const color = inlineTagColorInput.value;
            
            inlinePreviewText.textContent = name;
            const badge = inlineTagPreview.querySelector('.badge');
            if (badge) {
                badge.style.background = color;
            }
        }
    }

    async deleteTag(tagId) {
        const tag = this.tags.find(t => t.id === tagId);
        if (!tag) return;

        if (!confirm(`Êtes-vous sûr de vouloir supprimer l'étiquette "${tag.name}" ?`)) {
            return;
        }

        try {
            const csrfToken = this.getCSRFToken();
            
            console.log('🔄 Suppression du tag:', tagId);
            
            const response = await fetch(`/api/v1/core/tags/${tagId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                console.log('✅ Tag supprimé:', tagId);
                
                // Supprimer de la liste locale
                this.tags = this.tags.filter(t => t.id !== tagId);
                this.selectedTags.delete(tagId);
                
                // Cacher le formulaire inline si c'était le tag en cours d'édition
                if (this.inlineEditingTag && this.inlineEditingTag.id === tagId) {
                    this.cancelInlineEdit();
                }
                
                this.renderTags();
                this.updateTagsCount();
                this.showNotification(`Étiquette "${tag.name}" supprimée`, 'success');
            } else {
                console.error('❌ Erreur suppression:', response.status);
                const errorText = await response.text();
                console.error('❌ Détails:', errorText);
                this.showNotification('Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('❌ Erreur lors de la suppression du tag:', error);
            this.showNotification('Erreur lors de la suppression de l\'étiquette', 'error');
        }
    }

    async deleteSelectedTags() {
        if (this.selectedTags.size === 0) return;

        if (!confirm(`Êtes-vous sûr de vouloir supprimer ${this.selectedTags.size} étiquette(s) ?`)) {
            return;
        }

        try {
            const csrfToken = this.getCSRFToken();
            const tagsToDelete = Array.from(this.selectedTags);
            let deletedCount = 0;
            let errors = [];

            // Supprimer chaque tag individuellement
            for (const tagId of tagsToDelete) {
                try {
                    console.log('🔄 Suppression du tag (batch):', tagId);
                    
                    const response = await fetch(`/api/v1/core/tags/${tagId}/`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        credentials: 'same-origin'
                    });

                    if (response.ok) {
                        deletedCount++;
                        // Supprimer de la liste locale
                        this.tags = this.tags.filter(t => t.id !== tagId);
                        this.selectedTags.delete(tagId);
                        
                        // Cacher le formulaire inline si c'était le tag en cours d'édition
                        if (this.inlineEditingTag && this.inlineEditingTag.id === tagId) {
                            this.cancelInlineEdit();
                        }
                    } else {
                        const errorText = await response.text();
                        errors.push(`Tag ${tagId}: ${errorText}`);
                    }
                } catch (error) {
                    errors.push(`Tag ${tagId}: ${error.message}`);
                }
            }
            
            // Mettre à jour l'affichage
            this.selectedTags.clear();
            this.renderTags();
            this.updateTagsCount();
            
            // Afficher le résultat
            if (deletedCount === tagsToDelete.length) {
                this.showNotification(`${deletedCount} étiquette(s) supprimée(s)`, 'success');
            } else if (deletedCount > 0) {
                this.showNotification(`${deletedCount} étiquette(s) supprimée(s), ${errors.length} erreur(s)`, 'warning');
                console.error('Erreurs lors de la suppression batch:', errors);
            } else {
                this.showNotification('Erreur lors de la suppression des étiquettes', 'error');
                console.error('Erreurs lors de la suppression batch:', errors);
            }

        } catch (error) {
            console.error('❌ Erreur lors de la suppression batch des tags:', error);
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
            const csrfToken = this.getCSRFToken();
            
            if (this.editingTag) {
                // Modification - Appel API PUT
                console.log('🔄 Modification du tag:', this.editingTag.id);
                
                const response = await fetch(`/api/v1/core/tags/${this.editingTag.id}/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        name: tagName,
                        color: tagColor
                    })
                });

                if (response.ok) {
                    const updatedTag = await response.json();
                    console.log('✅ Tag modifié:', updatedTag);
                    
                    // Mettre à jour dans la liste locale
                    const tagIndex = this.tags.findIndex(t => t.id === this.editingTag.id);
                    if (tagIndex !== -1) {
                        this.tags[tagIndex] = {
                            ...this.tags[tagIndex],
                            name: updatedTag.name || updatedTag.display_name,
                            color: updatedTag.color
                        };
                    }
                    this.showNotification('Étiquette modifiée avec succès', 'success');
                } else {
                    console.error('❌ Erreur modification:', response.status);
                    const errorText = await response.text();
                    console.error('❌ Détails:', errorText);
                    this.showNotification('Erreur lors de la modification', 'error');
                    return; // Ne pas continuer si erreur
                }
            } else {
                // Création - Appel API POST
                console.log('🔄 Création nouveau tag:', tagName, tagColor);
                
                const response = await fetch('/api/v1/core/tags/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        name: tagName,
                        color: tagColor
                    })
                });

                if (response.ok) {
                    const newTag = await response.json();
                    console.log('✅ Nouveau tag créé:', newTag);
                    
                    // Ajouter à la liste locale
                    this.tags.push({
                        id: newTag.id,
                        name: newTag.name || newTag.display_name,
                        color: newTag.color,
                        description: newTag.description || '',
                        usage_count: newTag.usage_count_notebook || 0,
                        usage_count_total: newTag.usage_count_total || 0,
                        is_favorite: newTag.is_favorite || false,
                        created_at: newTag.created_at
                    });
                    this.showNotification('Étiquette créée avec succès', 'success');
                } else {
                    console.error('❌ Erreur création:', response.status);
                    const errorText = await response.text();
                    console.error('❌ Détails:', errorText);
                    this.showNotification('Erreur lors de la création', 'error');
                    return; // Ne pas continuer si erreur
                }
            }

            // Retourner à l'onglet liste
            const tagsListTab = document.getElementById('tags-list-tab');
            if (tagsListTab) {
                const tabTrigger = new bootstrap.Tab(tagsListTab);
                tabTrigger.show();
            }
            
            // Reset du formulaire
            this.cancelTagForm();

            // Recharger la liste
            this.renderTags();
            this.updateTagsCount();

        } catch (error) {
            console.error('❌ Erreur lors de la sauvegarde du tag:', error);
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
        const alertClass = type === 'error' ? 'danger' : 
                          type === 'success' ? 'success' : 
                          type === 'warning' ? 'warning' : 
                          'info';
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove après 5 secondes (plus long pour warnings)
        const timeout = type === 'warning' ? 8000 : 5000;
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, timeout);
    }
}

// Instancier la classe globalement
window.notebookTagsManagement = new NotebookTagsManagement();

// Initialiser au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    window.notebookTagsManagement.init();
});