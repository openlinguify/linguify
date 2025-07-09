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
        this.inputElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addTag(this.inputElement.value.trim());
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

    addTag(tagText) {
        if (!tagText || tagText.length === 0) {
            return false;
        }

        // Normaliser le tag
        const normalizedTag = this.normalizeTag(tagText);
        
        if (!this.isValidTag(normalizedTag)) {
            return false;
        }

        if (this.tags.has(normalizedTag)) {
            this.showError('Ce tag existe déjà');
            return false;
        }

        if (this.tags.size >= this.maxTags) {
            this.showError(`Maximum ${this.maxTags} tags autorisés`);
            return false;
        }

        this.tags.add(normalizedTag);
        this.availableTags.add(normalizedTag);
        this.inputElement.value = '';
        this.updateDisplay();
        this.hideSuggestions();
        return true;
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
                if (this.isValidTag(tag)) {
                    this.tags.add(this.normalizeTag(tag));
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
            item.addEventListener('click', () => {
                this.addTag(suggestion);
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
            }
        } catch (error) {
            console.error('Erreur lors du chargement des tags:', error);
        }
    }

    showError(message) {
        // Utiliser le système de notification existant
        if (window.notificationService) {
            window.notificationService.error(message);
        } else {
            console.error(message);
        }
    }
}

// Gestionnaire global des tags
window.tagsManager = new TagsManager();

// Fonction d'aide pour afficher les tags dans la liste des decks
function displayDeckTags(deck) {
    if (!deck.tags || deck.tags.length === 0) {
        return '<span class="no-tags-message">Aucun tag - Cliquez sur <i class="bi bi-tag"></i> pour en ajouter</span>';
    }

    // Couleurs des tags (style Odoo)
    const tagColors = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
        'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    ];

    return deck.tags.map((tag, index) => {
        const colorIndex = index % tagColors.length;
        return `<span class="deck-tag" style="background: ${tagColors[colorIndex]}">${tag}</span>`;
    }).join('');
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

        return selectedTags.every(tag => 
            deck.tags.some(deckTag => deckTag.toLowerCase() === tag.toLowerCase())
        );
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