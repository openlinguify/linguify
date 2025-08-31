// Revision Tags Management
class TagsManager {
    constructor() {
        this.tags = new Set();
        this.availableTags = new Set();
        this.maxTags = 10;
        this.maxTagLength = 50;
        this.inputElement = null;
        this.displayElement = null;
        this.suggestionsElement = null;
        this.isInitialized = false;
    }

    init(inputId, displayId) {
        this.inputElement = document.getElementById(inputId);
        this.displayElement = document.getElementById(displayId);
        
        if (!this.inputElement || !this.displayElement) {
            console.error('Tags manager: Input or display element not found');
            return;
        }

        this.setupEventListeners();
        this.isInitialized = true;
        this.loadAvailableTags();
    }

    setupEventListeners() {
        // Gestion de l'input
        this.inputElement.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                await this.addTag(this.inputElement.value.trim());
            } else if (e.key === 'Backspace' && this.inputElement.value === '') {
                this.removeLastTag();
            }
        });

        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });

        // Gestion du focus
        this.inputElement.addEventListener('focus', () => {
            this.inputElement.parentElement.classList.add('focused');
        });

        this.inputElement.addEventListener('blur', () => {
            this.inputElement.parentElement.classList.remove('focused');
            setTimeout(() => this.hideSuggestions(), 200);
        });
    }

    async addTag(tagText) {
        if (!tagText || tagText.length === 0) {
            return false;
        }

        // Normaliser le tag
        const normalizedTag = this.normalizeTag(tagText);
        const originalTag = tagText.trim();
        
        if (!this.isValidTag(normalizedTag)) {
            return false;
        }

        // 1. Vérifier si le tag existe déjà dans cette liste (case-insensitive)
        const existingTagInList = Array.from(this.tags).find(existingTag => 
            existingTag.trim().toLowerCase() === normalizedTag.toLowerCase()
        );
        
        if (existingTagInList) {
            this.showError(`Ce tag existe déjà dans cette liste: "${existingTagInList}"`);
            return false;
        }
        
        // 2. Vérification stricte contre les tags disponibles globaux
        await this.loadAvailableTags(); // S'assurer qu'on a les derniers tags
        
        const existingAvailableTag = Array.from(this.availableTags).find(availableTag => 
            availableTag.trim().toLowerCase() === normalizedTag.toLowerCase()
        );
        
        if (existingAvailableTag) {
            this.showError(`Ce tag existe déjà dans vos decks: "${existingAvailableTag}"`);
            return false;
        }

        if (this.tags.size >= this.maxTags) {
            this.showError(`Maximum ${this.maxTags} tags autorisés`);
            return false;
        }

        // 3. Validation finale via l'API (double sécurité)
        try {
            const response = await window.apiService.request('/api/v1/revision/tags/', {
                method: 'POST',
                body: JSON.stringify({ tag: normalizedTag })
            });
            
            // Si on arrive ici, le tag est validé par l'API
            this.tags.add(originalTag); // Garder la casse originale
            this.availableTags.add(originalTag); // Mettre à jour les tags disponibles
            this.inputElement.value = '';
            this.updateDisplay();
            this.hideSuggestions();
            
            console.log(`✅ Tag ajouté avec succès: "${originalTag}"`);
            return true;
            
        } catch (error) {
            if (error.status === 400) {
                // Erreur de validation par l'API (duplicate ou invalide)
                try {
                    const errorData = await error.response?.json?.() || {};
                    this.showError(errorData.detail || 'Ce tag ne peut pas être ajouté');
                } catch (parseError) {
                    this.showError('Ce tag ne peut pas être ajouté');
                }
            } else {
                console.error('Erreur API lors de la validation du tag:', error);
                this.showError('Erreur de connexion. Veuillez réessayer.');
            }
            return false;
        }
    }

    removeTag(tagText) {
        this.tags.delete(tagText);
        this.updateDisplay();
    }

    removeLastTag() {
        if (this.tags.size > 0) {
            const lastTag = Array.from(this.tags).pop();
            this.removeTag(lastTag);
        }
    }

    normalizeTag(tag) {
        return tag.trim().toLowerCase();
    }

    isValidTag(tag) {
        if (tag.length === 0) return false;
        if (tag.length > this.maxTagLength) {
            this.showError(`Le tag ne peut pas dépasser ${this.maxTagLength} caractères`);
            return false;
        }

        // Vérifier les caractères autorisés
        const validPattern = /^[a-zA-Z0-9àâäçéèêëïîôöùûüÿñæœ\s\-_]+$/;
        if (!validPattern.test(tag)) {
            this.showError('Le tag contient des caractères non autorisés');
            return false;
        }

        return true;
    }

    updateDisplay() {
        this.displayElement.innerHTML = '';
        
        this.tags.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag-item';
            tagElement.innerHTML = `
                <span>${tag}</span>
                <button type="button" class="tag-remove" onclick="window.tagsManager.removeTag('${tag}')">
                    <i class="bi bi-x"></i>
                </button>
            `;
            this.displayElement.appendChild(tagElement);
        });
    }

    getTags() {
        return Array.from(this.tags);
    }

    setTags(tags) {
        this.tags.clear();
        if (Array.isArray(tags)) {
            tags.forEach(tag => {
                if (this.isValidTag(tag.trim())) {
                    this.tags.add(tag.trim()); // Garder la casse originale, juste nettoyer les espaces
                }
            });
        }
        this.updateDisplay();
    }

    handleInput(value) {
        if (value.length > 0) {
            this.showSuggestions(value);
        } else {
            this.hideSuggestions();
        }
    }

    showSuggestions(query) {
        if (!this.suggestionsElement) {
            this.createSuggestionsElement();
        }

        const suggestions = this.getSuggestions(query);
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsElement.innerHTML = '';
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'tags-suggestion-item';
            item.textContent = suggestion;
            item.addEventListener('click', async () => {
                await this.addTag(suggestion);
            });
            this.suggestionsElement.appendChild(item);
        });

        this.suggestionsElement.style.display = 'block';
    }

    hideSuggestions() {
        if (this.suggestionsElement) {
            this.suggestionsElement.style.display = 'none';
        }
    }

    getSuggestions(query) {
        const normalizedQuery = query.toLowerCase();
        return Array.from(this.availableTags)
            .filter(tag => 
                tag.includes(normalizedQuery) && 
                !this.tags.has(tag)
            )
            .slice(0, 5);
    }

    createSuggestionsElement() {
        this.suggestionsElement = document.createElement('div');
        this.suggestionsElement.className = 'tags-suggestions';
        this.suggestionsElement.style.display = 'none';
        
        // Positionner par rapport au conteneur parent
        const container = this.inputElement.parentElement;
        container.style.position = 'relative';
        container.appendChild(this.suggestionsElement);
    }

    async loadAvailableTags() {
        try {
            const response = await window.apiService.request('/api/v1/revision/tags/');
            if (response && response.tags) {
                this.availableTags = new Set(response.tags);
                console.log(`🔄 Tags disponibles rechargés: ${response.tags.length} tags`);
                return true;
            } else {
                console.warn('Réponse API tags invalide:', response);
                return false;
            }
        } catch (error) {
            console.error('Erreur lors du chargement des tags:', error);
            return false;
        }
    }

    showError(message) {
        // Utiliser le système de notification existant
        if (window.notificationService) {
            window.notificationService.error(message);
        } else {
            console.error(message);
            // Fallback: afficher une alerte si pas de système de notification
            alert(message);
        }
    }
    
    // Méthode de debug pour diagnostiquer les problèmes
    debugTagsState(action = '') {
        console.group(`Debug Tags State ${action ? '- ' + action : ''}`);
        console.log('Tags actuels dans la liste:', Array.from(this.tags));
        console.log('Tags disponibles globaux:', Array.from(this.availableTags));
        console.log('Input value:', this.inputElement?.value || 'N/A');
        console.groupEnd();
    }
}

// Gestionnaire global des tags
window.tagsManager = new TagsManager();

// Fonction d'aide pour afficher les tags dans la liste des decks
function displayDeckTags(deck) {
    console.log('displayDeckTags appelé pour deck:', deck.name, 'Tags:', deck.tags);
    
    if (!deck.tags || deck.tags.length === 0) {
        const noTagsHTML = createNoTagsElement(deck.id);
        console.log('Retour HTML pour aucun tag:', noTagsHTML);
        return noTagsHTML;
    }

    // Classes Tailwind pour les couleurs des tags (style Linguify)
    const tagClasses = [
        'tag-linguify-purple',
        'tag-linguify-pink',
        'tag-linguify-blue',
        'tag-linguify-green',
        'tag-linguify-orange',
        'tag-linguify-teal',
        'tag-linguify-yellow',
        'tag-linguify-indigo'
    ];

    const tagsHTML = deck.tags.map((tag, index) => {
        return createTagElement(tag, tagClasses[index % tagClasses.length]);
    }).join('');
    
    console.log('Retour HTML pour tags existants:', tagsHTML);
    return tagsHTML;
}

// Créer l'élément "Aucun tag" - Version simplifiée et robuste
function createNoTagsElement(deckId) {
    console.log('createNoTagsElement appelé pour deck ID:', deckId);
    console.log('Fonction quickEditTags existe:', typeof quickEditTags !== 'undefined');
    
    // Version directe et robuste avec icône plus visible
    const htmlContent = `<span class="no-tags-message">Aucun tag - Cliquez sur <i class="bi bi-tag" onclick="event.stopPropagation(); console.log('Clic sur icône tag, deck:', ${deckId}); if(typeof quickEditTags !== 'undefined') { quickEditTags(${deckId}); } else { console.error('quickEditTags non définie'); }" style="cursor: pointer; color: #2d5bba; font-size: 1rem; margin: 0 4px; font-weight: bold; background: #f0f9ff; padding: 2px 4px; border-radius: 3px;">🏷️</i> pour en ajouter</span>`;
    
    console.log('HTML généré:', htmlContent);
    return htmlContent;
}

// Créer un élément tag à partir du template
function createTagElement(tagName, tagClass) {
    const template = document.getElementById('tag-template');
    if (!template) {
        console.error('Template tag-template non trouvé');
        return `<span class="tag-linguify ${tagClass}">${tagName}</span>`;
    }
    
    const clone = template.content.cloneNode(true);
    const span = clone.querySelector('.tag-linguify');
    if (span) {
        span.textContent = tagName;
        span.classList.add(tagClass);
    }
    
    // Retourner le HTML comme string pour compatibilité
    const div = document.createElement('div');
    div.appendChild(clone);
    return div.innerHTML;
}

// Fonction d'aide pour filtrer les decks par tags
function filterDecksByTags(decks, selectedTags) {
    if (!selectedTags || selectedTags.length === 0) {
        return decks;
    }

    return decks.filter(deck => {
        if (!deck.tags || deck.tags.length === 0) {
            return false;
        }

        // Utilise OR logic: le deck doit avoir AU MOINS UN des tags sélectionnés
        return selectedTags.some(selectedTag => {
            const normalizedSelectedTag = selectedTag.trim().toLowerCase();
            return deck.tags.some(deckTag => {
                const normalizedDeckTag = deckTag.trim().toLowerCase();
                return normalizedDeckTag === normalizedSelectedTag;
            });
        });
    });
}

// Fonction pour créer un filtre de tags
function createTagsFilter(containerSelector, onTagsChange) {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    const tagsFilter = document.createElement('div');
    tagsFilter.className = 'tags-filter';
    tagsFilter.innerHTML = '<div class="text-muted small mb-2">Filtrer par tags:</div>';

    // Charger tous les tags disponibles
    loadAllTags().then(tags => {
        tags.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag-filter-item';
            tagElement.textContent = tag;
            tagElement.addEventListener('click', () => {
                tagElement.classList.toggle('active');
                const activeTags = Array.from(tagsFilter.querySelectorAll('.tag-filter-item.active'))
                    .map(el => el.textContent);
                onTagsChange(activeTags);
            });
            tagsFilter.appendChild(tagElement);
        });
    });

    container.appendChild(tagsFilter);
}

// Fonction pour charger tous les tags disponibles
async function loadAllTags() {
    try {
        const response = await window.apiService.request('/api/v1/revision/tags/');
        return response.tags || [];
    } catch (error) {
        console.error('Erreur lors du chargement des tags:', error);
        return [];
    }
}

// Export pour utilisation dans d'autres modules
window.TagsManager = TagsManager;
window.displayDeckTags = displayDeckTags;
window.filterDecksByTags = filterDecksByTags;
window.createTagsFilter = createTagsFilter;