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

        // Nouveau tag
        const createNewTagBtn = document.getElementById('createNewTagBtn');
        if (createNewTagBtn) {
            createNewTagBtn.addEventListener('click', () => this.showCreateTagModal());
        }

        // Sélection de tous les tags
        const selectAllTags = document.getElementById('selectAllTags');
        if (selectAllTags) {
            selectAllTags.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
        }

        // Suppression des tags sélectionnés
        const deleteSelectedTagsBtn = document.getElementById('deleteSelectedTagsBtn');
        if (deleteSelectedTagsBtn) {
            deleteSelectedTagsBtn.addEventListener('click', () => this.deleteSelectedTags());
        }

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
            modal.classList.add('show');
            document.body.classList.add('modal-open');
            
            // Ajouter overlay
            if (!document.querySelector('.modal-backdrop')) {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                backdrop.addEventListener('click', () => this.closeTagsManagement());
                document.body.appendChild(backdrop);
                console.log('✅ Backdrop ajouté');
            }
            
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
            modal.classList.add('show');
            
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
            
            tagPreview.innerHTML = `<span class="badge" style="background: ${color}; color: white;">${name}</span>`;
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
        
        this.renderTagsInternal(tbody);
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

        const htmlContent = paginatedTags.map(tag => `
            <tr class="tag-row ${this.assignedTags.has(tag.name) ? 'table-success' : ''}" data-tag="${tag.name}">
                <td>
                    <input type="checkbox" class="form-check-input tag-assign-checkbox" 
                           data-tag="${tag.name}" ${this.assignedTags.has(tag.name) ? 'checked' : ''}>
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
                        <button class="btn btn-outline-primary" onclick="window.tagsManagement.editTag('${tag.name}')" title="Modifier">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="window.tagsManagement.deleteTag('${tag.name}')" title="Supprimer">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
        
        console.log('🎨 HTML généré pour', paginatedTags.length, 'tags:', htmlContent.substring(0, 200) + '...');
        tbody.innerHTML = htmlContent;

        // Event listeners pour les checkboxes d'assignation
        const checkboxes = tbody.querySelectorAll('.tag-assign-checkbox');
        console.log('🎨 Attachement des event listeners sur', checkboxes.length, 'checkboxes');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const tagName = e.target.dataset.tag;
                const row = e.target.closest('tr');
                
                if (e.target.checked) {
                    this.assignedTags.add(tagName);
                    row.classList.add('table-success');
                } else {
                    this.assignedTags.delete(tagName);
                    row.classList.remove('table-success');
                }
                
                // Sauvegarder les changements immédiatement
                this.saveTagsToCurrentDeck();
            });
        });

        this.renderPagination(filteredTags.length);
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
            tagsCount.textContent = `${this.tags.length} étiquette(s)`;
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
            modal.classList.remove('show');
            document.body.classList.remove('modal-open');
            
            // Supprimer backdrop
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        }
    }

    closeCreateTagModal() {
        const modal = document.getElementById('tagEditModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
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

    createTagsModal() {
        console.log('🔨 Création de la modal HTML...');
        
        const modalHTML = `
        <div class="modal fade" id="tagsManagementModal" tabindex="-1" aria-labelledby="tagsManagementModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="tagsManagementModalLabel">
                            <i class="bi bi-tags me-2"></i>Gestion des étiquettes
                        </h5>
                        <button type="button" class="btn-close" onclick="window.tagsManagement.closeTagsManagement()" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Barre de recherche -->
                        <div class="row mb-3">
                            <div class="col-md-8">
                                <div class="input-group">
                                    <span class="input-group-text">
                                        <i class="bi bi-search"></i>
                                    </span>
                                    <input type="text" id="tagsSearchInput" class="form-control" placeholder="Rechercher une étiquette...">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <button id="createNewTagBtn" class="btn btn-primary w-100">
                                    <i class="bi bi-plus-lg me-1"></i>Nouvelle étiquette
                                </button>
                            </div>
                        </div>

                        <!-- Liste des tags -->
                        <div class="tags-management-container">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 50px;">
                                                <input type="checkbox" id="selectAllTags" class="form-check-input">
                                            </th>
                                            <th>Nom</th>
                                            <th style="width: 80px;">Couleur</th>
                                            <th style="width: 100px;">Utilisations</th>
                                            <th style="width: 120px;">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="tagsTableBody">
                                        <!-- Les tags seront chargés dynamiquement ici -->
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- Pagination -->
                        <nav aria-label="Pagination des tags">
                            <ul class="pagination justify-content-center" id="tagsPagination">
                                <!-- Pagination sera générée dynamiquement -->
                            </ul>
                        </nav>
                    </div>
                    <div class="modal-footer">
                        <div class="d-flex w-100 justify-content-between align-items-center">
                            <div>
                                <button type="button" class="btn btn-primary" id="selectTagsBtn">
                                    <i class="bi bi-check-lg me-1"></i>Sélectionner
                                </button>
                                <button type="button" class="btn btn-success ms-2" id="createNewTagFromModal">
                                    <i class="bi bi-plus-lg me-1"></i>Nouveau
                                </button>
                            </div>
                            <div class="d-flex align-items-center gap-3">
                                <span id="tagsCount" class="text-muted">0 étiquette(s)</span>
                                <button type="button" class="btn btn-secondary" onclick="window.tagsManagement.closeTagsManagement()">Fermer</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Modal de création/édition d'étiquette -->
        <div class="modal fade" id="tagEditModal" tabindex="-1" aria-labelledby="tagEditModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="tagEditModalLabel">Nouvelle étiquette</h5>
                        <button type="button" class="btn-close" onclick="window.tagsManagement.closeCreateTagModal()" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="tagEditForm">
                            <div class="mb-3">
                                <label for="tagNameInput" class="form-label">Nom de l'étiquette *</label>
                                <input type="text" class="form-control" id="tagNameInput" required maxlength="50">
                                <div class="form-text">Utilisez des noms courts et descriptifs</div>
                            </div>
                            <div class="mb-3">
                                <label for="tagColorInput" class="form-label">Couleur</label>
                                <div class="d-flex align-items-center gap-2">
                                    <input type="color" class="form-control form-control-color" id="tagColorInput" value="#667eea">
                                    <div class="tag-preview" id="tagPreview">
                                        <span class="badge" style="background: #667eea; color: white;">Aperçu</span>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="window.tagsManagement.closeCreateTagModal()">Annuler</button>
                        <button type="button" class="btn btn-primary" id="saveTagBtn">
                            <i class="bi bi-check-lg me-1"></i>Enregistrer
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Créer un container temporaire pour parser le HTML
        const container = document.createElement('div');
        container.innerHTML = modalHTML;
        
        // Ajouter toutes les modals au body
        while (container.firstChild) {
            document.body.appendChild(container.firstChild);
        }
        
        // Réattacher les event listeners après création
        this.attachDynamicEventListeners();
        
        console.log('✅ Modal créée et ajoutée au DOM');
        return document.getElementById('tagsManagementModal');
    }

    attachDynamicEventListeners() {
        // Event listeners qui étaient attachés dans setupEventListeners mais pour la modal dynamique
        
        // Recherche
        const searchInput = document.getElementById('tagsSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.renderTags();
            });
        }

        // Nouveau tag
        const createNewTagBtn = document.getElementById('createNewTagBtn');
        if (createNewTagBtn) {
            createNewTagBtn.addEventListener('click', () => this.showCreateTagModal());
        }

        // Sélection de tous les tags
        const selectAllTags = document.getElementById('selectAllTags');
        if (selectAllTags) {
            selectAllTags.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
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
    window.tagsManagement.init();
    console.log('✅ TagsManagement initialisé');
});