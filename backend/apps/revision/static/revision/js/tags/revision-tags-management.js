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

        // Le bouton "Créer" est maintenant géré par le formulaire quickCreateTagForm

        // Les fonctionnalités de sélection multiple ont été supprimées dans le nouveau design
        // Plus simple et plus épuré comme dans Notebook

        // Les fonctionnalités d'édition de tag sont maintenant intégrées au formulaire principal

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
            <td style="padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle;">
                <span style="width: 14px; height: 14px; border-radius: 50%; display: inline-block; margin-right: 8px; background-color: ${tag.color};"></span>
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle;">
                <span style="font-weight: 500; color: #111827; cursor: pointer;">${tag.name}</span>
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle;">
                <span style="font-size: 0.875rem; color: #6b7280;">${tag.usage_count}</span>
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle;">
                <span style="font-size: 0.875rem; color: #6b7280;">${createdDate}</span>
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; text-align: center; width: 100px;">
                <button style="background: none; border: none; padding: 6px; border-radius: 4px; color: #6b7280; cursor: pointer; transition: all 0.2s; margin: 0 2px;" 
                        onmouseover="this.style.background='#f3f4f6'; this.style.color='#374151';" 
                        onmouseout="this.style.background='none'; this.style.color='#6b7280';"
                        title="Modifier" onclick="window.tagsManagement.editTag('${tag.name}')">
                    <i class="bi bi-pencil"></i>
                </button>
                <button style="background: none; border: none; padding: 6px; border-radius: 4px; color: #6b7280; cursor: pointer; transition: all 0.2s; margin: 0 2px;" 
                        onmouseover="this.style.background='#fef2f2'; this.style.color='#dc2626';" 
                        onmouseout="this.style.background='none'; this.style.color='#6b7280';"
                        title="Supprimer" onclick="window.tagsManagement.deleteTag('${tag.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        
        // Ajouter un event listener pour la sélection de tag (clic sur le nom)
        const tagNameElement = row.querySelector('td:nth-child(2) span');
        if (tagNameElement) {
            tagNameElement.addEventListener('click', () => {
                this.toggleTagAssignment(tag.name, row);
            });
        }
        
        // Ajouter les effets hover et la sélection
        row.addEventListener('mouseenter', () => {
            if (!row.classList.contains('tag-assigned')) {
                row.style.backgroundColor = '#fafbfc';
            }
        });
        
        row.addEventListener('mouseleave', () => {
            if (!row.classList.contains('tag-assigned')) {
                row.style.backgroundColor = '';
            }
        });
        
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

    // Méthode pour gérer le formulaire intégré (création ET modification)
    async handleQuickCreateTag() {
        const quickTagName = document.getElementById('quickTagName');
        const quickTagColor = document.getElementById('quickTagColor');
        const createBtn = document.getElementById('createNewTagBtn');
        
        if (!quickTagName || !quickTagColor) return;
        
        const tagName = quickTagName.value.trim();
        const tagColor = quickTagColor.value;
        
        if (!tagName) {
            window.notificationService?.error('Le nom de l\'étiquette est requis');
            return;
        }

        try {
            if (this.editingTag) {
                // MODE ÉDITION
                await this.updateTagInAllDecks(this.editingTag.name, tagName);
                window.notificationService?.success('Étiquette modifiée avec succès');
                
                // Remettre le bouton en mode création
                this.resetFormToCreateMode();
            } else {
                // MODE CRÉATION
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
                    
                    // Actualiser l'affichage du deck
                    if (this.currentDeckId && window.renderDecksList) {
                        window.renderDecksList();
                    }
                } else {
                    throw new Error('Validation du tag échouée');
                }
            }
            
            // Réinitialiser le formulaire
            quickTagName.value = '';
            quickTagColor.value = '#3b82f6';
            this.updateQuickTagPreview();
            
            // Recharger la liste depuis le serveur
            await this.loadTags();

        } catch (error) {
            console.error('Erreur lors de la sauvegarde du tag:', error);
            let errorMessage = this.editingTag ? 'Erreur lors de la modification de l\'étiquette' : 'Erreur lors de la création de l\'étiquette';
            
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

    // Remettre le formulaire en mode création
    resetFormToCreateMode() {
        const createBtn = document.getElementById('createNewTagBtn');
        if (createBtn) {
            createBtn.textContent = 'Créer';
            createBtn.style.background = '#3b82f6';
        }
        this.editingTag = null;
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
            // Utiliser le formulaire intégré pour l'édition
            const quickTagName = document.getElementById('quickTagName');
            const quickTagColor = document.getElementById('quickTagColor');
            const createBtn = document.getElementById('createNewTagBtn');
            
            if (quickTagName && quickTagColor && createBtn) {
                // Pré-remplir le formulaire
                quickTagName.value = tag.name;
                quickTagColor.value = tag.color;
                this.updateQuickTagPreview();
                
                // Changer le bouton en mode édition
                createBtn.textContent = 'Modifier';
                createBtn.style.background = '#f59e0b';
                
                // Mettre le tag en mode édition
                this.editingTag = tag;
                
                // Focus sur l'input
                quickTagName.focus();
                quickTagName.select();
                
                // Scroll vers le formulaire
                document.getElementById('quickCreateTagForm').scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
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