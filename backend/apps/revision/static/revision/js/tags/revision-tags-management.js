// Gestion des tags - Interface style OpenLinguify
class TagsManagement {
    constructor() {
        this.tags = [];
        this.selectedTags = new Set(); // Tags sélectionnés pour suppression en lot
        this.assignedTags = new Set(); // Tags assignés au deck courant
        this.currentDeckId = null; // ID du deck en cours d'édition
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.searchQuery = '';
        this.editingTag = null;
        this.colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c', 
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
            '#fa709a', '#fee140', '#a8edea', '#fed6e3',
            '#ffecd2', '#fcb69f', '#667eea', '#764ba2'
        ];
    }

    init() {
        this.setupEventListeners();
        this.loadTags(false); // false = ne pas render lors de l'init
    }

    setupEventListeners() {
        // Le bouton de gestion des tags est maintenant dans la modal quick-tags
        // Il est géré par la fonction openTagsManagementFromQuick() dans revision-main.js

        // Recherche
        const searchInput = document.getElementById('tagsSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.renderTags();
            });
        }

        // Quick create form - nouvelle approche style Notebook
        const quickCreateForm = document.getElementById('quickCreateTagForm');
        if (quickCreateForm) {
            quickCreateForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleQuickCreateTag();
            });
        }

        // Aperçu en temps réel pour le quick create
        const quickTagName = document.getElementById('quickTagName');
        const quickTagColor = document.getElementById('quickTagColor');
        if (quickTagName && quickTagColor) {
            quickTagName.addEventListener('input', () => this.updateQuickTagPreview());
            quickTagColor.addEventListener('input', () => this.updateQuickTagPreview());
        }

        // Nouveau tag (bouton modal séparée)
        const createNewTagBtn = document.getElementById('createNewTagBtn');
        if (createNewTagBtn) {
            createNewTagBtn.addEventListener('click', () => this.showCreateTagModal());
        }

        // Les fonctionnalités de sélection multiple ont été supprimées dans le nouveau design
        // Plus simple et plus épuré comme dans Notebook

        // Sauvegarde du tag (création/édition)
        const saveTagBtn = document.getElementById('saveTagBtn');
        if (saveTagBtn) {
            saveTagBtn.addEventListener('click', () => this.saveTag());
        }

        // Aperçu couleur
        const tagColorInput = document.getElementById('tagColorInput');
        const tagNameInput = document.getElementById('tagNameInput');
        if (tagColorInput && tagNameInput) {
            tagColorInput.addEventListener('input', () => this.updateTagPreview());
            tagNameInput.addEventListener('input', () => this.updateTagPreview());
        }

        // Validation du formulaire
        const tagEditForm = document.getElementById('tagEditForm');
        if (tagEditForm) {
            tagEditForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveTag();
            });
        }

        // Boutons style OpenLinguify
        const selectTagsBtn = document.getElementById('selectTagsBtn');
        if (selectTagsBtn) {
            selectTagsBtn.addEventListener('click', () => this.closeTagsManagement());
        }

        const createNewTagFromModal = document.getElementById('createNewTagFromModal');
        if (createNewTagFromModal) {
            createNewTagFromModal.addEventListener('click', () => this.showCreateTagModal());
        }
    }

    setCurrentDeck(deckId) {
        this.currentDeckId = parseInt(deckId);
        console.log('🎯 setCurrentDeck appelé avec deckId:', this.currentDeckId);
        
        // Charger les tags du deck courant
        if (window.appState && window.appState.decks) {
            const deck = window.appState.decks.find(d => d.id === this.currentDeckId);
            if (deck && deck.tags) {
                this.assignedTags = new Set(deck.tags);
                console.log('📋 Tags assignés au deck:', this.assignedTags);
            } else {
                this.assignedTags = new Set();
                console.log('📋 Aucun tag assigné au deck');
            }
        }
    }

    async showTagsManagement() {
        console.log('🎯 showTagsManagement appelé pour deck:', this.currentDeckId);
        
        let modal = document.getElementById('tagsManagementModal');
        console.log('🔍 Modal trouvée:', modal ? 'OUI' : 'NON');
        
        if (!modal) {
            console.error('❌ Modal tags non trouvée dans le DOM. Vérifiez que le partiel est inclus.');
            return;
        }
        
        this.updateModalTitle();
        
        // Charger les tags APRÈS avoir créé la modal
        await this.loadTags();
        
        if (modal) {
            console.log('📋 Affichage de la modal...');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
            console.log('✅ Modal affichée !');
        } else {
            console.error('❌ Impossible de créer la modal !');
        }
    }

    updateModalTitle() {
        const modalTitle = document.getElementById('tagsManagementModalLabel');
        if (modalTitle && this.currentDeckId && window.appState) {
            const deck = window.appState.decks.find(d => d.id === this.currentDeckId);
            if (deck) {
                modalTitle.innerHTML = `<i class="bi bi-tags me-2"></i>Étiquettes pour "${deck.name}"`;
            }
        }
    }

    showCreateTagModal(tagData = null) {
        this.editingTag = tagData;
        
        const modal = document.getElementById('tagEditModal');
        const modalTitle = document.getElementById('tagEditModalLabel');
        const tagNameInput = document.getElementById('tagNameInput');
        const tagColorInput = document.getElementById('tagColorInput');

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
        
        // Afficher la modal
        if (modal) {
            modal.style.display = 'block';
            
            // Focus sur le nom
            setTimeout(() => tagNameInput.focus(), 300);
        }
    }

    updateTagPreview() {
        const tagNameInput = document.getElementById('tagNameInput');
        const tagColorInput = document.getElementById('tagColorInput');
        const tagPreview = document.getElementById('tagPreview');

        if (tagNameInput && tagColorInput && tagPreview) {
            const name = tagNameInput.value || 'Aperçu';
            const color = tagColorInput.value;
            
            // Utiliser les classes tailwind-modals.css
            const badge = tagPreview.querySelector('.tag-color-preview');
            if (badge) {
                badge.textContent = name;
                badge.style.background = color;
                badge.style.color = 'white';
            } else {
                // Fallback
                tagPreview.innerHTML = `<span class="tag-badge-linguify" style="background: ${color}; color: white;">${name}</span>`;
            }
        }
    }

    getRandomColor() {
        return this.colors[Math.floor(Math.random() * this.colors.length)];
    }

    async loadTags(shouldRender = true) {
        console.log('📡 Chargement des tags...');
        
        try {
            const response = await window.apiService.request('/api/v1/revision/tags/', {
                method: 'GET'
            });

            console.log('📋 Réponse API tags:', response);

            if (response && response.tags) {
                // Enrichir les tags avec des couleurs et calculer les comptages réels
                this.tags = await Promise.all(response.tags.map(async (tag, index) => {
                    const usageCount = await this.getTagUsageCount(tag);
                    return {
                        name: tag,
                        color: this.colors[index % this.colors.length],
                        usage_count: usageCount
                    };
                }));
                console.log('✅ Tags traités:', this.tags);
            } else {
                this.tags = [];
                console.log('⚠️ Aucun tag trouvé dans la réponse');
            }

            if (shouldRender) {
                this.renderTags();
                this.updateTagsCount();
            }

        } catch (error) {
            console.error('❌ Erreur lors du chargement des tags:', error);
            window.notificationService?.error('Erreur lors du chargement des étiquettes');
        }
    }

    async getTagUsageCount(tagName) {
        try {
            // Compter l'utilisation du tag dans les decks de l'utilisateur
            if (window.appState && window.appState.decks) {
                return window.appState.decks.filter(deck => 
                    deck.tags && deck.tags.some(tag => 
                        tag.toLowerCase() === tagName.toLowerCase()
                    )
                ).length;
            }
            return 0;
        } catch (error) {
            console.error('Erreur lors du calcul de l\'usage du tag:', error);
            return 0;
        }
    }

    renderTags() {
        const tbody = document.getElementById('tagsTableBody');
        const emptyState = document.getElementById('tagsEmptyState');
        const table = document.getElementById('tagsTable');
        
        console.log('🎨 renderTags: tbody trouvé:', tbody ? 'OUI' : 'NON');
        console.log('🎨 renderTags: nombre de tags à afficher:', this.tags.length);
        
        if (!tbody) {
            console.error('❌ Élément tagsTableBody non trouvé dans le DOM');
            // Retry after a short delay to allow DOM to be ready
            setTimeout(() => {
                const retryTbody = document.getElementById('tagsTableBody');
                if (retryTbody) {
                    console.log('✅ Retry successful: tagsTableBody found after delay');
                    this.renderTagsInternal(retryTbody);
                } else {
                    console.error('❌ Retry failed: tagsTableBody still not found');
                }
            }, 100);
            return;
        }
        
        // Gérer l'état vide style Notebook
        if (this.tags.length === 0) {
            if (table) table.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
        } else {
            if (table) table.style.display = 'table';
            if (emptyState) emptyState.style.display = 'none';
            this.renderTagsInternal(tbody);
        }
    }
    
    renderTagsInternal(tbody) {

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

        // Vider le tbody
        tbody.innerHTML = '';
        
        // Créer les lignes de tags à partir du template
        paginatedTags.forEach(tag => {
            const row = this.createTagTableRow(tag);
            tbody.appendChild(row);
        });

        // Les event listeners pour les tags sont maintenant gérés dans createTagTableRow()
        // via les clics sur le nom du tag (plus simple et moderne)

        this.renderPagination(filteredTags.length);
    }

    // Créer une ligne de tag dans le tableau - style Notebook simplifié
    createTagTableRow(tag) {
        const row = document.createElement('tr');
        row.className = 'tag-row';
        row.dataset.tag = tag.name;
        
        // Calculer la date de création (placeholder)
        const createdDate = new Date().toLocaleDateString();
        
        row.innerHTML = `
            <td>
                <span class="tag-dot" style="background-color: ${tag.color};"></span>
            </td>
            <td>
                <span class="tag-name">${tag.name}</span>
            </td>
            <td>
                <span class="tags-usage-count">${tag.usage_count}</span>
            </td>
            <td>
                <span class="tags-usage-count">${createdDate}</span>
            </td>
            <td class="tags-actions-cell">
                <button class="tags-action-btn" title="Modifier" onclick="window.tagsManagement.editTag('${tag.name}')">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="tags-action-btn delete" title="Supprimer" onclick="window.tagsManagement.deleteTag('${tag.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        
        // Ajouter un event listener pour la sélection de tag (clic sur le nom)
        const tagNameElement = row.querySelector('.tag-name');
        if (tagNameElement) {
            tagNameElement.addEventListener('click', () => {
                this.toggleTagAssignment(tag.name, row);
            });
        }
        
        // Marquer visuellement si le tag est assigné au deck courant
        if (this.assignedTags.has(tag.name)) {
            row.classList.add('tag-assigned');
            row.style.backgroundColor = '#f0f9ff';
            row.style.borderLeft = `3px solid ${tag.color}`;
        }
        
        return row;
    }

    // Nouvelle méthode pour basculer l'assignation d'un tag
    toggleTagAssignment(tagName, rowElement) {
        if (this.assignedTags.has(tagName)) {
            this.assignedTags.delete(tagName);
            rowElement.classList.remove('tag-assigned');
            rowElement.style.backgroundColor = '';
            rowElement.style.borderLeft = '';
        } else {
            this.assignedTags.add(tagName);
            rowElement.classList.add('tag-assigned');
            rowElement.style.backgroundColor = '#f0f9ff';
            const tag = this.tags.find(t => t.name === tagName);
            if (tag) {
                rowElement.style.borderLeft = `3px solid ${tag.color}`;
            }
        }
        
        // Sauvegarder les changements immédiatement
        this.saveTagsToCurrentDeck();
    }

    renderPagination(totalItems) {
        const pagination = document.getElementById('tagsPagination');
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
                <a class="page-link" href="#" onclick="window.tagsManagement.goToPage(${this.currentPage - 1})">Précédent</a>
            </li>
        `;

        // Numéros de pages
        for (let i = 1; i <= totalPages; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="window.tagsManagement.goToPage(${i})">${i}</a>
                </li>
            `;
        }

        // Bouton suivant
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.tagsManagement.goToPage(${this.currentPage + 1})">Suivant</a>
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
        const tagsCount = document.getElementById('tagsCount');
        if (tagsCount) {
            tagsCount.textContent = this.tags.length;
        }
    }

    // Nouvelle méthode pour gérer le quick create form style Notebook
    async handleQuickCreateTag() {
        const quickTagName = document.getElementById('quickTagName');
        const quickTagColor = document.getElementById('quickTagColor');
        
        if (!quickTagName || !quickTagColor) return;
        
        const tagName = quickTagName.value.trim();
        const tagColor = quickTagColor.value;
        
        if (!tagName) {
            window.notificationService?.error('Le nom de l\'étiquette est requis');
            return;
        }

        try {
            // Valider le tag via l'API
            const validationResponse = await window.apiService.request('/api/v1/revision/tags/', {
                method: 'POST',
                body: JSON.stringify({ tag: tagName })
            });
            
            if (validationResponse && validationResponse.tag) {
                // Ajouter automatiquement le nouveau tag au deck courant
                if (this.currentDeckId) {
                    this.assignedTags.add(tagName);
                    await this.saveTagsToCurrentDeck();
                }
                
                // Réinitialiser le formulaire
                quickTagName.value = '';
                quickTagColor.value = '#3b82f6';
                this.updateQuickTagPreview();
                
                window.notificationService?.success('Étiquette créée et ajoutée au deck');
                
                // Recharger la liste depuis le serveur
                await this.loadTags();
                
                // Actualiser l'affichage du deck
                if (this.currentDeckId && window.renderDecksList) {
                    window.renderDecksList();
                }
            } else {
                throw new Error('Validation du tag échouée');
            }

        } catch (error) {
            console.error('Erreur lors de la création du tag:', error);
            let errorMessage = 'Erreur lors de la création de l\'étiquette';
            
            // Gérer les erreurs spécifiques de validation
            if (error.status === 400) {
                try {
                    const errorData = await error.response?.json?.() || {};
                    errorMessage = errorData.detail || 'Cette étiquette ne peut pas être ajoutée';
                } catch (parseError) {
                    errorMessage = 'Cette étiquette ne peut pas être ajoutée';
                }
            }
            
            window.notificationService?.error(errorMessage);
        }
    }

    // Mettre à jour l'aperçu du quick create
    updateQuickTagPreview() {
        const quickTagName = document.getElementById('quickTagName');
        const quickTagColor = document.getElementById('quickTagColor');
        const quickPreviewText = document.getElementById('quickPreviewText');
        const quickTagPreview = document.getElementById('quickTagPreview');
        
        if (quickTagName && quickTagColor && quickPreviewText && quickTagPreview) {
            const name = quickTagName.value.trim() || 'Aperçu';
            const color = quickTagColor.value;
            
            quickPreviewText.textContent = name;
            const badge = quickTagPreview.querySelector('.tag-badge-linguify');
            if (badge) {
                badge.style.backgroundColor = color;
            }
        }
    }

    updateDeleteButton() {
        const deleteBtn = document.getElementById('deleteSelectedTagsBtn');
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
            
            paginatedTags.forEach(tag => this.selectedTags.add(tag.name));
        }

        this.renderTags();
        this.updateDeleteButton();
    }

    editTag(tagName) {
        const tag = this.tags.find(t => t.name === tagName);
        if (tag) {
            this.showCreateTagModal(tag);
        }
    }

    async deleteTag(tagName) {
        const usageCount = await this.getTagUsageCount(tagName);
        
        let confirmMessage = `Êtes-vous sûr de vouloir supprimer l'étiquette "${tagName}" ?`;
        if (usageCount > 0) {
            confirmMessage += `\n\nCette étiquette est utilisée dans ${usageCount} deck(s). Elle sera supprimée de tous ces decks.`;
        }
        
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            // Supprimer le tag de tous les decks qui l'utilisent
            await this.removeTagFromAllDecks(tagName);
            
            window.notificationService?.success(`Étiquette "${tagName}" supprimée de ${usageCount} deck(s)`);
            
            // Recharger la liste depuis le serveur
            await this.loadTags();

        } catch (error) {
            console.error('Erreur lors de la suppression du tag:', error);
            window.notificationService?.error('Erreur lors de la suppression de l\'étiquette');
        }
    }

    async removeTagFromAllDecks(tagName) {
        if (!window.appState || !window.appState.decks) return;
        
        // Trouver tous les decks qui utilisent ce tag
        const decksToUpdate = window.appState.decks.filter(deck => 
            deck.tags && deck.tags.some(tag => 
                tag.toLowerCase() === tagName.toLowerCase()
            )
        );
        
        // Supprimer le tag de chaque deck
        for (const deck of decksToUpdate) {
            try {
                const updatedTags = deck.tags.filter(tag => 
                    tag.toLowerCase() !== tagName.toLowerCase()
                );
                
                await window.revisionAPI.updateDeck(deck.id, { tags: updatedTags });
                
                // Mettre à jour l'état local
                deck.tags = updatedTags;
            } catch (error) {
                console.error(`Erreur lors de la mise à jour du deck ${deck.id}:`, error);
            }
        }
        
        // Actualiser l'affichage des decks
        if (window.renderDecksList) {
            window.renderDecksList();
        }
    }

    async deleteSelectedTags() {
        if (this.selectedTags.size === 0) return;

        const tagsToDelete = Array.from(this.selectedTags);
        
        // Calculer l'usage total
        let totalUsage = 0;
        for (const tagName of tagsToDelete) {
            totalUsage += await this.getTagUsageCount(tagName);
        }
        
        let confirmMessage = `Êtes-vous sûr de vouloir supprimer ${tagsToDelete.length} étiquette(s) ?`;
        if (totalUsage > 0) {
            confirmMessage += `\n\nCes étiquettes sont utilisées dans un total de ${totalUsage} deck(s). Elles seront supprimées de tous ces decks.`;
        }
        
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            // Supprimer chaque tag
            let successCount = 0;
            for (const tagName of tagsToDelete) {
                try {
                    await this.removeTagFromAllDecks(tagName);
                    successCount++;
                } catch (error) {
                    console.error(`Erreur lors de la suppression du tag ${tagName}:`, error);
                }
            }
            
            this.selectedTags.clear();
            
            if (successCount === tagsToDelete.length) {
                window.notificationService?.success(`${successCount} étiquette(s) supprimée(s) avec succès`);
            } else {
                window.notificationService?.error(`${successCount}/${tagsToDelete.length} étiquette(s) supprimée(s). Certaines suppressions ont échoué.`);
            }
            
            // Recharger la liste depuis le serveur
            await this.loadTags();

        } catch (error) {
            console.error('Erreur lors de la suppression des tags:', error);
            window.notificationService?.error('Erreur lors de la suppression des étiquettes');
        }
    }

    async saveTag() {
        const tagNameInput = document.getElementById('tagNameInput');
        const tagColorInput = document.getElementById('tagColorInput');

        if (!tagNameInput || !tagColorInput) return;

        const tagName = tagNameInput.value.trim();
        const tagColor = tagColorInput.value;

        if (!tagName) {
            window.notificationService?.error('Le nom de l\'étiquette est requis');
            return;
        }

        try {
            if (this.editingTag) {
                // Modification - mettre à jour tous les decks qui utilisent ce tag
                await this.updateTagInAllDecks(this.editingTag.name, tagName);
                window.notificationService?.success('Étiquette modifiée avec succès');
            } else {
                // Création - valider le tag via l'API
                const validationResponse = await window.apiService.request('/api/v1/revision/tags/', {
                    method: 'POST',
                    body: JSON.stringify({ tag: tagName })
                });
                
                if (validationResponse && validationResponse.tag) {
                    // Ajouter automatiquement le nouveau tag au deck courant
                    if (this.currentDeckId) {
                        this.assignedTags.add(tagName);
                        await this.saveTagsToCurrentDeck();
                    }
                    window.notificationService?.success('Étiquette créée et ajoutée au deck');
                } else {
                    throw new Error('Validation du tag échouée');
                }
            }

            // Fermer la modal
            this.closeCreateTagModal();

            // Recharger la liste depuis le serveur
            await this.loadTags();
            
            // Actualiser l'affichage du deck si on a créé et assigné un tag
            if (!this.editingTag && this.currentDeckId && window.renderDecksList) {
                window.renderDecksList();
            }

        } catch (error) {
            console.error('Erreur lors de la sauvegarde du tag:', error);
            let errorMessage = 'Erreur lors de la sauvegarde de l\'étiquette';
            
            // Gérer les erreurs spécifiques de validation
            if (error.message && error.message.includes('existe déjà')) {
                errorMessage = 'Cette étiquette existe déjà';
            } else if (error.message && error.message.includes('caractères')) {
                errorMessage = 'Le nom de l\'étiquette contient des caractères invalides';
            } else if (error.message && error.message.includes('long')) {
                errorMessage = 'Le nom de l\'étiquette est trop long (50 caractères maximum)';
            }
            
            window.notificationService?.error(errorMessage);
        }
    }

    async updateTagInAllDecks(oldTagName, newTagName) {
        if (!window.appState || !window.appState.decks) return;
        
        // Trouver tous les decks qui utilisent l'ancien tag
        const decksToUpdate = window.appState.decks.filter(deck => 
            deck.tags && deck.tags.some(tag => 
                tag.toLowerCase() === oldTagName.toLowerCase()
            )
        );
        
        // Mettre à jour chaque deck
        for (const deck of decksToUpdate) {
            try {
                const updatedTags = deck.tags.map(tag => 
                    tag.toLowerCase() === oldTagName.toLowerCase() ? newTagName : tag
                );
                
                await window.revisionAPI.updateDeck(deck.id, { tags: updatedTags });
                
                // Mettre à jour l'état local
                deck.tags = updatedTags;
            } catch (error) {
                console.error(`Erreur lors de la mise à jour du deck ${deck.id}:`, error);
            }
        }
        
        // Actualiser l'affichage des decks
        if (window.renderDecksList) {
            window.renderDecksList();
        }
    }

    closeTagsManagement() {
        const modal = document.getElementById('tagsManagementModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    }

    closeCreateTagModal() {
        const modal = document.getElementById('tagEditModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async saveTagsToCurrentDeck() {
        if (!this.currentDeckId || !window.revisionAPI) {
            console.log('⚠️ saveTagsToCurrentDeck: currentDeckId ou revisionAPI manquant', this.currentDeckId);
            return;
        }

        try {
            const tagsArray = Array.from(this.assignedTags);
            console.log('💾 Sauvegarde des tags pour le deck', this.currentDeckId, ':', tagsArray);
            
            // Sauvegarder via l'API
            await window.revisionAPI.updateDeck(this.currentDeckId, { tags: tagsArray });
            
            // Mettre à jour l'état local
            if (window.appState && window.appState.decks) {
                const deck = window.appState.decks.find(d => d.id === this.currentDeckId);
                console.log('🔍 Deck trouvé dans appState:', deck ? deck.name : 'NON TROUVÉ');
                if (deck) {
                    deck.tags = tagsArray;
                    console.log('📝 Tags mis à jour dans le deck:', deck.tags);
                    
                    // Actualiser l'affichage de la liste des decks
                    if (window.renderDecksList) {
                        console.log('🔄 Actualisation de la liste des decks...');
                        window.renderDecksList();
                    }
                }
            }
            
            console.log('✅ Tags sauvegardés pour le deck', this.currentDeckId);
            
        } catch (error) {
            console.error('Erreur lors de la sauvegarde des tags:', error);
            window.notificationService?.error('Erreur lors de la sauvegarde des tags');
        }
    }

}

// Instancier la classe globalement
window.tagsManagement = new TagsManagement();

// Fonction de test pour vérifier que tout est bien chargé
window.testTagsManagement = function() {
    console.log('🧪 Test de gestion des tags:');
    console.log('- tagsManagement existe:', !!window.tagsManagement);
    console.log('- Modal existe:', !!document.getElementById('tagsManagementModal'));
    console.log('- apiService existe:', !!window.apiService);
    
    if (window.tagsManagement) {
        console.log('🎯 Test d\'ouverture de la modal...');
        window.tagsManagement.showTagsManagement();
    }
};

// Initialiser au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initialisation TagsManagement...');
    console.log('🔍 Modal trouvée:', !!document.getElementById('tagsManagementModal'));
    console.log('🔍 window.tagsManagement existe:', !!window.tagsManagement);
    window.tagsManagement.init();
    console.log('✅ TagsManagement initialisé');
});