/**
 * Explore New JS - Interface moderne pour la page Explorer
 * Gestion avancée des filtres, recherche intelligente, et interactions UI
 * Version améliorée avec UX parfaite
 */

// ===== VARIABLES GLOBALES =====
const ExploreApp = {
    currentFilters: new Map(),
    searchHistory: [],
    favorites: new Set(),
    collections: new Map(),
    currentView: 'grid',
    sortBy: 'relevance',
    sortOrder: 'desc',
    currentPage: 1,
    resultsPerPage: 20,
    isLoading: false,
    searchDebounceTimer: null,
    lastSearchQuery: '',
    totalResults: 0
};

// ===== INITIALISATION MODERNE ===== 
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation de l\'interface Explorer moderne...');
    
    // Initialiser tous les composants
    initSidebar();
    initSearch();
    initFilters();
    initViewModes();
    initNotifications();
    initCollections();
    initPagination();
    
    // Charger les données initiales
    loadInitialData();
    
    console.log('✅ Interface Explorer moderne prête');
});

// ===== GESTION DE LA SIDEBAR MODERNE =====
function initSidebar() {
    const sidebar = document.getElementById('exploreSidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const collapseBtn = document.getElementById('collapseSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    // Toggle sidebar
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            toggleSidebar();
        });
    }
    
    // Collapse sidebar
    if (collapseBtn) {
        collapseBtn.addEventListener('click', function() {
            sidebar?.classList.remove('show');
            overlay?.classList.remove('active');
            updateToggleButtonState(false);
        });
    }
    
    // Overlay click
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar?.classList.remove('show');
            overlay.classList.remove('active');
            updateToggleButtonState(false);
        });
    }
    
    // Initialiser les sections collapsibles
    initCollapsibleSections();
}

function toggleSidebar() {
    const sidebar = document.getElementById('exploreSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!sidebar) return;
    
    const isVisible = sidebar.classList.contains('show');
    
    if (isVisible) {
        sidebar.classList.remove('show');
        overlay?.classList.remove('active');
        updateToggleButtonState(false);
    } else {
        sidebar.classList.add('show');
        overlay?.classList.add('active');
        updateToggleButtonState(true);
    }
}

function updateToggleButtonState(isActive) {
    const toggleBtn = document.getElementById('sidebarToggle');
    if (toggleBtn) {
        toggleBtn.classList.toggle('active', isActive);
    }
}

function initCollapsibleSections() {
    const sectionHeaders = document.querySelectorAll('.section-header[data-toggle]');
    
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-toggle');
            const content = document.getElementById(sectionId + 'Content') || 
                          document.getElementById(sectionId + 'Filters') ||
                          document.getElementById(sectionId.replace('advanced', 'advancedFilters'));
            
            if (content) {
                const isExpanded = !content.classList.contains('collapsed');
                content.classList.toggle('collapsed');
                this.classList.toggle('expanded', !isExpanded);
                
                // Sauvegarder l'état dans localStorage
                localStorage.setItem(`sidebar_${sectionId}_expanded`, !isExpanded);
            }
        });
        
        // Restaurer l'état sauvegardé
        const sectionId = header.getAttribute('data-toggle');
        const savedState = localStorage.getItem(`sidebar_${sectionId}_expanded`);
        if (savedState === 'false') {
            const content = document.getElementById(sectionId + 'Content') || 
                          document.getElementById(sectionId + 'Filters');
            if (content) {
                content.classList.add('collapsed');
                header.classList.remove('expanded');
            }
        } else {
            header.classList.add('expanded');
        }
    });
}

// ===== RECHERCHE INTELLIGENTE MODERNE =====
function initSearch() {
    const searchInput = document.getElementById('exploreSearchInput');
    const suggestionsContainer = document.getElementById('searchSuggestions');
    const voiceBtn = document.getElementById('voiceSearchBtn');
    const aiBtn = document.getElementById('aiSearchBtn');
    
    if (!searchInput) return;
    
    // Event listeners pour la recherche
    searchInput.addEventListener('input', handleSearchInput);
    searchInput.addEventListener('focus', showSearchSuggestions);
    searchInput.addEventListener('blur', hideSearchSuggestions);
    searchInput.addEventListener('keydown', handleSearchKeydown);
    
    // Voice search
    if (voiceBtn) {
        voiceBtn.addEventListener('click', startVoiceSearch);
    }
    
    // AI search
    if (aiBtn) {
        aiBtn.addEventListener('click', triggerAISearch);
    }
    
    // Quick suggestions
    initQuickSuggestions();
}

function handleSearchInput(event) {
    const query = event.target.value.trim();
    
    // Debounce la recherche
    if (ExploreApp.searchDebounceTimer) {
        clearTimeout(ExploreApp.searchDebounceTimer);
    }
    
    ExploreApp.searchDebounceTimer = setTimeout(() => {
        if (query.length >= 2) {
            updateSearchSuggestions(query);
            performLiveSearch(query);
        } else if (query.length === 0) {
            clearResults();
            showWelcomeScreen();
        }
    }, 300);
}

function updateSearchSuggestions(query) {
    const container = document.getElementById('smartSuggestions');
    if (!container) return;
    
    // Simuler des suggestions intelligentes
    const suggestions = generateSmartSuggestions(query);
    
    if (suggestions.length > 0) {
        container.style.display = 'block';
        const itemsContainer = document.getElementById('aiSuggestions');
        if (itemsContainer) {
            itemsContainer.innerHTML = suggestions.map(suggestion => `
                <div class="suggestion-item smart" data-query="${suggestion.query}">
                    <div class="suggestion-content">
                        <span class="suggestion-text">${suggestion.text}</span>
                        <span class="suggestion-count">${suggestion.count} résultats</span>
                    </div>
                    <i class="bi bi-stars"></i>
                </div>
            `).join('');
            
            // Event listeners pour les suggestions
            itemsContainer.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', function() {
                    const query = this.getAttribute('data-query');
                    performSearch(query);
                    hideSearchSuggestions();
                });
            });
        }
    }
}

function generateSmartSuggestions(query) {
    const suggestions = [];
    const lowerQuery = query.toLowerCase();
    
    // Suggestions basées sur des patterns courants
    if (lowerQuery.includes('anglais') || lowerQuery.includes('english')) {
        suggestions.push({
            query: 'vocabulaire anglais b2',
            text: 'Vocabulaire anglais B2',
            count: '2.1k'
        });
    }
    
    if (lowerQuery.includes('math') || lowerQuery.includes('calcul')) {
        suggestions.push({
            query: 'mathématiques lycée',
            text: 'Mathématiques lycée',
            count: '1.8k'
        });
    }
    
    return suggestions;
}

function startVoiceSearch() {
    if (!('webkitSpeechRecognition' in window)) {
        showNotification('Recherche vocale non supportée', 'warning');
        return;
    }
    
    const recognition = new webkitSpeechRecognition();
    const voiceBtn = document.getElementById('voiceSearchBtn');
    
    recognition.lang = 'fr-FR';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    voiceBtn?.classList.add('listening');
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('exploreSearchInput').value = transcript;
        performSearch(transcript);
    };
    
    recognition.onerror = function() {
        showNotification('Erreur de reconnaissance vocale', 'error');
    };
    
    recognition.onend = function() {
        voiceBtn?.classList.remove('listening');
    };
    
    recognition.start();
}

function triggerAISearch() {
    const query = document.getElementById('exploreSearchInput')?.value;
    if (!query) return;
    
    // Simuler une recherche IA intelligente
    showNotification('Recherche IA en cours...', 'info');
    
    setTimeout(() => {
        performSearch(query + ' (recherche intelligente)');
        showNotification('Recherche IA terminée', 'success');
    }, 1500);
}

function initQuickSuggestions() {
    const quickSuggestions = document.querySelectorAll('.quick-suggestion');
    
    quickSuggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            const query = this.getAttribute('data-search');
            document.getElementById('exploreSearchInput').value = query;
            performSearch(query);
        });
    });
}

// ===== GESTION DES FILTRES MODERNES =====
function initFilters() {
    initQuickFilters();
    initAdvancedFilters();
    initFilterActions();
}

function initQuickFilters() {
    const quickFilters = document.querySelectorAll('.filter-chip');
    
    quickFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // Désactiver les autres filtres rapides
            quickFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            
            // Appliquer le filtre
            if (category === 'all') {
                ExploreApp.currentFilters.clear();
            } else {
                ExploreApp.currentFilters.set('category', category);
            }
            
            applyFilters();
            updateActiveFiltersDisplay();
        });
    });
}

function initAdvancedFilters() {
    // Filtres de langue
    const languageOptions = document.querySelectorAll('.language-option');
    languageOptions.forEach(option => {
        option.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            
            languageOptions.forEach(o => o.classList.remove('active'));
            this.classList.add('active');
            
            if (lang === 'all') {
                ExploreApp.currentFilters.delete('language');
            } else {
                ExploreApp.currentFilters.set('language', lang);
            }
            
            updateActiveFiltersDisplay();
        });
    });
    
    // Filtres de niveau
    const levelBtns = document.querySelectorAll('.level-btn');
    levelBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const level = this.getAttribute('data-level');
            
            levelBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (level === 'all') {
                ExploreApp.currentFilters.delete('level');
            } else {
                ExploreApp.currentFilters.set('level', level);
            }
            
            updateActiveFiltersDisplay();
        });
    });
    
    // Filtres de rating
    const starBtns = document.querySelectorAll('.star-btn');
    starBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const rating = this.getAttribute('data-rating');
            
            starBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (rating === '0') {
                ExploreApp.currentFilters.delete('rating');
            } else {
                ExploreApp.currentFilters.set('rating', rating);
            }
            
            updateActiveFiltersDisplay();
        });
    });
    
    // Range presets
    const presetBtns = document.querySelectorAll('.preset-btn');
    presetBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const range = this.getAttribute('data-range');
            
            presetBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Parser le range et mettre à jour les inputs
            if (range === '1-20') {
                document.getElementById('minCards').value = '1';
                document.getElementById('maxCards').value = '20';
            } else if (range === '21-50') {
                document.getElementById('minCards').value = '21';
                document.getElementById('maxCards').value = '50';
            } else if (range === '51+') {
                document.getElementById('minCards').value = '51';
                document.getElementById('maxCards').value = '';
            }
            
            ExploreApp.currentFilters.set('cardRange', range);
            updateActiveFiltersDisplay();
        });
    });
}

function initFilterActions() {
    const applyBtn = document.getElementById('applyFilters');
    const clearBtn = document.getElementById('clearFilters');
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            applyFilters();
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            clearAllFilters();
        });
    }
}

function updateActiveFiltersDisplay() {
    const display = document.getElementById('activeFiltersDisplay');
    const countElement = document.getElementById('activeFiltersCount');
    const listElement = document.getElementById('activeFiltersList');
    
    if (!display || !countElement || !listElement) return;
    
    const activeCount = ExploreApp.currentFilters.size;
    
    if (activeCount > 0) {
        display.style.display = 'block';
        countElement.style.display = 'flex';
        countElement.querySelector('.count-badge').textContent = activeCount;
        
        // Afficher les filtres actifs
        const filterElements = [];
        ExploreApp.currentFilters.forEach((value, key) => {
            filterElements.push(`
                <div class="active-filter-chip" data-filter="${key}">
                    <span>${getFilterDisplayName(key, value)}</span>
                    <button class="remove-filter" data-filter="${key}">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            `);
        });
        
        listElement.innerHTML = filterElements.join('');
        
        // Event listeners pour supprimer les filtres
        listElement.querySelectorAll('.remove-filter').forEach(btn => {
            btn.addEventListener('click', function() {
                const filterKey = this.getAttribute('data-filter');
                ExploreApp.currentFilters.delete(filterKey);
                updateActiveFiltersDisplay();
                applyFilters();
            });
        });
    } else {
        display.style.display = 'none';
        countElement.style.display = 'none';
    }
}

function getFilterDisplayName(key, value) {
    const displayNames = {
        category: {
            languages: '🌍 Langues',
            science: '🧬 Sciences',
            technology: '💻 Tech',
            math: '📐 Mathématiques'
        },
        language: {
            fr: '🇫🇷 Français',
            en: '🇺🇸 Anglais',
            es: '🇪🇸 Espagnol'
        },
        level: {
            beginner: '🟢 Débutant',
            intermediate: '🟡 Intermédiaire',
            advanced: '🔴 Avancé'
        }
    };
    
    return displayNames[key]?.[value] || `${key}: ${value}`;
}

function applyFilters() {
    const applyBtn = document.getElementById('applyFilters');
    const loading = document.getElementById('loadingDecks');
    
    // Afficher l'état de chargement
    if (applyBtn) {
        const btnLoading = applyBtn.querySelector('.btn-loading');
        if (btnLoading) {
            btnLoading.style.display = 'flex';
        }
        applyBtn.disabled = true;
    }
    
    if (loading) {
        loading.style.display = 'block';
    }
    
    // Simuler l'application des filtres
    setTimeout(() => {
        performSearch(ExploreApp.lastSearchQuery);
        
        // Cacher l'état de chargement
        if (applyBtn) {
            const btnLoading = applyBtn.querySelector('.btn-loading');
            if (btnLoading) {
                btnLoading.style.display = 'none';
            }
            applyBtn.disabled = false;
        }
        
        if (loading) {
            loading.style.display = 'none';
        }
        
        showNotification('Filtres appliqués', 'success');
    }, 1000);
}

function clearAllFilters() {
    ExploreApp.currentFilters.clear();
    
    // Réinitialiser tous les éléments de filtre
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.classList.remove('active');
        if (chip.getAttribute('data-category') === 'all') {
            chip.classList.add('active');
        }
    });
    
    document.querySelectorAll('.language-option').forEach(option => {
        option.classList.remove('active');
        if (option.getAttribute('data-lang') === 'all') {
            option.classList.add('active');
        }
    });
    
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-level') === 'all') {
            btn.classList.add('active');
        }
    });
    
    // Vider les inputs
    const minCards = document.getElementById('minCards');
    const maxCards = document.getElementById('maxCards');
    const authorFilter = document.getElementById('authorFilter');
    
    if (minCards) minCards.value = '';
    if (maxCards) maxCards.value = '';
    if (authorFilter) authorFilter.value = '';
    
    updateActiveFiltersDisplay();
    applyFilters();
}

// ===== NOTIFICATION CENTER =====
function toggleNotificationCenter() {
    const center = document.getElementById('notificationCenter');
    const overlay = document.getElementById('notificationOverlay');
    const isVisible = center && center.style.display !== 'none';
    
    if (isVisible) {
        hideNotificationCenter();
    } else {
        showNotificationCenter();
    }
}

function showNotificationCenter() {
    const center = document.getElementById('notificationCenter');
    const overlay = document.getElementById('notificationOverlay');
    
    if (center) center.style.display = 'block';
    if (overlay) overlay.classList.add('show');
}

// ===== GESTION DES VUES =====
function initViewModes() {
    const viewModeButtons = document.querySelectorAll('.view-mode-btn');
    
    viewModeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const viewMode = this.getAttribute('data-view');
            switchViewMode(viewMode);
        });
    });
    
    // Initialiser le tri
    const sortSelect = document.getElementById('sortBy');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            ExploreApp.sortBy = this.value;
            applySort();
        });
    }
    
    const sortOrderBtn = document.getElementById('sortOrder');
    if (sortOrderBtn) {
        sortOrderBtn.addEventListener('click', function() {
            ExploreApp.sortOrder = ExploreApp.sortOrder === 'desc' ? 'asc' : 'desc';
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = ExploreApp.sortOrder === 'desc' ? 'bi bi-sort-down' : 'bi bi-sort-up';
            }
            applySort();
        });
    }
}

function switchViewMode(mode) {
    ExploreApp.currentView = mode;
    
    // Update button states
    document.querySelectorAll('.view-mode-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-view') === mode) {
            btn.classList.add('active');
        }
    });
    
    // Switch display
    const containers = {
        grid: document.getElementById('publicDecksGrid'),
        list: document.getElementById('publicDecksList'),
        compact: document.getElementById('publicDecksCompact')
    };
    
    Object.keys(containers).forEach(key => {
        const container = containers[key];
        if (container) {
            container.style.display = key === mode ? 'block' : 'none';
        }
    });
    
    // Save preference
    localStorage.setItem('explorer_view_mode', mode);
}

function applySort() {
    // Simuler le tri des résultats
    showNotification(`Tri par ${ExploreApp.sortBy} (${ExploreApp.sortOrder})`, 'info');
    
    // Ici on rechargerait les résultats avec le nouveau tri
    setTimeout(() => {
        refreshResults();
    }, 500);
}

// ===== GESTION DES COLLECTIONS =====
function initCollections() {
    const createBtn = document.getElementById('createCollectionBtn');
    if (createBtn) {
        createBtn.addEventListener('click', function() {
            showCreateCollectionModal();
        });
    }
    
    loadUserCollections();
    loadUserFavorites();
}

function loadUserCollections() {
    // Simuler le chargement des collections
    const container = document.getElementById('myCollections');
    if (!container) return;
    
    // Exemple de collections
    const collections = [
        { id: 1, name: 'Langues Européennes', count: 12, description: 'Collection de vocabulaire' },
        { id: 2, name: 'Sciences & Tech', count: 8, description: 'Termes scientifiques' }
    ];
    
    if (collections.length > 0) {
        container.innerHTML = collections.map(collection => `
            <div class="collection-item" data-id="${collection.id}">
                <div class="collection-icon">
                    <i class="bi bi-collection"></i>
                </div>
                <div class="collection-info">
                    <div class="collection-name">${collection.name}</div>
                    <div class="collection-description">${collection.description}</div>
                </div>
                <div class="collection-count">${collection.count}</div>
            </div>
        `).join('');
        
        // Update counter
        const counter = document.getElementById('myCollectionsCount');
        if (counter) counter.textContent = collections.length;
    }
}

function loadUserFavorites() {
    // Simuler le chargement des favoris
    const container = document.getElementById('favoriteDecks');
    const counter = document.getElementById('favoritesCount');
    
    if (!container || !counter) return;
    
    // Exemple de favoris
    const favorites = [
        { id: 1, title: 'Vocabulaire Anglais B2', author: '@sarah_lang' },
        { id: 2, title: 'Mathématiques Terminale', author: '@prof_math' }
    ];
    
    if (favorites.length > 0) {
        container.innerHTML = favorites.map(fav => `
            <div class="favorite-item" data-id="${fav.id}">
                <div class="favorite-icon">
                    <i class="bi bi-heart-fill"></i>
                </div>
                <div class="favorite-info">
                    <div class="favorite-title">${fav.title}</div>
                    <div class="favorite-author">${fav.author}</div>
                </div>
            </div>
        `).join('');
        
        counter.textContent = favorites.length;
        
        // Montrer le bouton "Voir tous"
        const viewAllBtn = document.getElementById('viewAllFavorites');
        if (viewAllBtn && favorites.length > 3) {
            viewAllBtn.style.display = 'flex';
        }
    } else {
        counter.textContent = '0';
    }
}

// ===== GESTION DE LA PAGINATION =====
function initPagination() {
    const infiniteScrollToggle = document.getElementById('infiniteScroll');
    const resultsPerPageSelect = document.getElementById('resultsPerPage');
    
    if (infiniteScrollToggle) {
        infiniteScrollToggle.addEventListener('change', function() {
            if (this.checked) {
                enableInfiniteScroll();
            } else {
                disableInfiniteScroll();
            }
        });
    }
    
    if (resultsPerPageSelect) {
        resultsPerPageSelect.addEventListener('change', function() {
            ExploreApp.resultsPerPage = parseInt(this.value);
            refreshResults();
        });
    }
}

function enableInfiniteScroll() {
    // Implémenter le scroll infini
    window.addEventListener('scroll', handleInfiniteScroll);
}

function disableInfiniteScroll() {
    window.removeEventListener('scroll', handleInfiniteScroll);
}

function handleInfiniteScroll() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
        if (!ExploreApp.isLoading && ExploreApp.currentPage * ExploreApp.resultsPerPage < ExploreApp.totalResults) {
            loadMoreResults();
        }
    }
}

// ===== FONCTIONS UTILITAIRES =====
function performSearch(query) {
    ExploreApp.lastSearchQuery = query;
    ExploreApp.currentPage = 1;
    
    // Afficher les résultats
    showResultsScreen();
    showLoadingState();
    
    // Simuler la recherche
    setTimeout(() => {
        hideLoadingState();
        displaySearchResults(generateMockResults(query));
        updateSearchHistory(query);
    }, 1000);
}

function generateMockResults(query) {
    const mockResults = [
        {
            id: 1,
            title: 'Vocabulaire Anglais B2',
            description: 'Collection complète de vocabulaire pour le niveau B2',
            author: 'sarah_lang',
            cardsCount: 250,
            rating: 4.8,
            downloads: 1200,
            category: 'languages',
            level: 'intermediate'
        },
        {
            id: 2,
            title: 'Mathématiques Terminale S',
            description: 'Toutes les formules et définitions importantes',
            author: 'prof_math',
            cardsCount: 180,
            rating: 4.6,
            downloads: 800,
            category: 'math',
            level: 'advanced'
        }
    ];
    
    // Filtrer selon les critères actuels
    return mockResults.filter(result => {
        if (ExploreApp.currentFilters.has('category')) {
            return result.category === ExploreApp.currentFilters.get('category');
        }
        return true;
    });
}

function displaySearchResults(results) {
    ExploreApp.totalResults = results.length;
    
    // Mettre à jour le compteur
    const countElement = document.getElementById('resultsCount');
    if (countElement) countElement.textContent = results.length;
    
    // Afficher les résultats selon le mode de vue
    const container = document.getElementById('publicDecksGrid');
    if (!container) return;
    
    if (results.length === 0) {
        showNoResults();
        return;
    }
    
    container.innerHTML = results.map(result => generateDeckCard(result)).join('');
    
    // Initialiser les interactions des cartes
    initCardInteractions();
}

function generateDeckCard(deck) {
    return `
        <div class="deck-card-modern" data-id="${deck.id}">
            <div class="deck-card-header">
                <div class="deck-category">${getCategoryIcon(deck.category)}</div>
                <div class="deck-actions">
                    <button class="deck-action-btn favorite-btn" title="Ajouter aux favoris">
                        <i class="bi bi-heart"></i>
                    </button>
                    <button class="deck-action-btn collection-btn" title="Ajouter à une collection">
                        <i class="bi bi-plus-circle"></i>
                    </button>
                </div>
            </div>
            <div class="deck-card-content">
                <h3 class="deck-title">${deck.title}</h3>
                <p class="deck-description">${deck.description}</p>
                <div class="deck-meta">
                    <div class="deck-author">
                        <i class="bi bi-person-circle"></i>
                        <span>@${deck.author}</span>
                    </div>
                    <div class="deck-stats">
                        <span class="stat"><i class="bi bi-stack"></i> ${deck.cardsCount}</span>
                        <span class="stat"><i class="bi bi-star-fill"></i> ${deck.rating}</span>
                        <span class="stat"><i class="bi bi-download"></i> ${deck.downloads}</span>
                    </div>
                </div>
            </div>
            <div class="deck-card-footer">
                <button class="btn-import-deck" onclick="importDeck(${deck.id})">
                    <i class="bi bi-download"></i>
                    <span>Importer</span>
                </button>
                <button class="btn-preview-deck" onclick="previewDeck(${deck.id})">
                    <i class="bi bi-eye"></i>
                    <span>Aperçu</span>
                </button>
            </div>
        </div>
    `;
}

function getCategoryIcon(category) {
    const icons = {
        languages: '🌍',
        science: '🧬',
        math: '📐',
        technology: '💻',
        history: '📜'
    };
    return icons[category] || '📋';
}

function showResultsScreen() {
    document.getElementById('exploreWelcome')?.setAttribute('style', 'display: none');
    document.getElementById('exploreResults')?.setAttribute('style', 'display: block');
}

function showWelcomeScreen() {
    document.getElementById('exploreWelcome')?.setAttribute('style', 'display: block');
    document.getElementById('exploreResults')?.setAttribute('style', 'display: none');
}

function showLoadingState() {
    document.getElementById('loadingDecks')?.setAttribute('style', 'display: block');
    document.getElementById('publicDecksGrid')?.setAttribute('style', 'display: none');
}

function hideLoadingState() {
    document.getElementById('loadingDecks')?.setAttribute('style', 'display: none');
    document.getElementById('publicDecksGrid')?.setAttribute('style', 'display: block');
}

function showNoResults() {
    document.getElementById('noResults')?.setAttribute('style', 'display: block');
    document.getElementById('publicDecksGrid')?.setAttribute('style', 'display: none');
}

function showNotification(message, type = 'info') {
    // Implémenter le système de notifications toast
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function loadInitialData() {
    // Charger les statistiques globales
    setTimeout(() => {
        document.getElementById('totalDecksCount').textContent = '2.1k';
        document.getElementById('totalCardsCount').textContent = '156k';
        document.getElementById('totalAuthorsCount').textContent = '847';
        document.getElementById('weeklyActivity').textContent = '+23';
        document.getElementById('totalDecksDisplay').textContent = '2,156';
    }, 500);
}

// ===== FONCTIONS D'IMPORT ET PREVIEW =====
function importDeck(deckId) {
    showNotification(`Import du deck ${deckId} en cours...`, 'info');
    
    setTimeout(() => {
        showNotification('Deck importé avec succès !', 'success');
    }, 1500);
}

function previewDeck(deckId) {
    showNotification(`Aperçu du deck ${deckId}`, 'info');
}

function initNotifications() {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationCenter = document.getElementById('notificationCenter');
    const overlay = document.getElementById('notificationOverlay');
    
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function() {
            toggleNotificationCenter();
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', function() {
            hideNotificationCenter();
        });
    }
    
    // Initialiser les filtres de notifications
    initNotificationFilters();
}

function initNotificationFilters() {
    const filters = document.querySelectorAll('.notification-filter');
    const items = document.querySelectorAll('.notification-item');
    
    filters.forEach(filter => {
        filter.addEventListener('click', function() {
            // Remove active class from all filters
            filters.forEach(f => f.classList.remove('active'));
            // Add active class to clicked filter
            this.classList.add('active');
            
            const filterType = this.getAttribute('data-filter');
            
            // Show/hide notifications based on filter
            items.forEach(item => {
                const itemType = item.getAttribute('data-type');
                if (filterType === 'all' || itemType === filterType) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

function hideNotificationCenter() {
    const center = document.getElementById('notificationCenter');
    const overlay = document.getElementById('notificationOverlay');
    
    if (center) center.style.display = 'none';
    if (overlay) overlay.classList.remove('show');
}

// ===== GESTION DES INTERACTIONS CARTES =====
function initCardInteractions() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    const collectionButtons = document.querySelectorAll('.collection-btn');
    
    favoriteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleFavorite(this);
        });
    });
    
    collectionButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            showAddToCollectionModal(this.closest('.deck-card-modern').getAttribute('data-id'));
        });
    });
}

function toggleFavorite(btn) {
    const isFavorited = btn.classList.contains('favorited');
    
    if (isFavorited) {
        btn.classList.remove('favorited');
        btn.querySelector('i').className = 'bi bi-heart';
        btn.classList.add('animate-favorite');
        showNotification('Retiré des favoris', 'info');
    } else {
        btn.classList.add('favorited');
        btn.querySelector('i').className = 'bi bi-heart-fill';
        btn.classList.add('animate-favorite');
        showNotification('Ajouté aux favoris', 'success');
    }
    
    setTimeout(() => btn.classList.remove('animate-favorite'), 600);
}

// ===== FONCTIONS UTILITAIRES SUPPLÉMENTAIRES =====
function refreshResults() {
    if (ExploreApp.lastSearchQuery) {
        performSearch(ExploreApp.lastSearchQuery);
    }
}

function clearResults() {
    document.getElementById('publicDecksGrid').innerHTML = '';
    document.getElementById('resultsCount').textContent = '0';
}

function updateSearchHistory(query) {
    if (query && !ExploreApp.searchHistory.includes(query)) {
        ExploreApp.searchHistory.unshift(query);
        if (ExploreApp.searchHistory.length > 10) {
            ExploreApp.searchHistory.pop();
        }
        localStorage.setItem('explore_search_history', JSON.stringify(ExploreApp.searchHistory));
    }
}

function showSearchSuggestions() {
    document.getElementById('searchSuggestions')?.setAttribute('style', 'display: block');
}

function hideSearchSuggestions() {
    setTimeout(() => {
        document.getElementById('searchSuggestions')?.setAttribute('style', 'display: none');
    }, 200);
}

function handleSearchKeydown(event) {
    if (event.key === 'Enter') {
        const query = event.target.value.trim();
        if (query) {
            performSearch(query);
            hideSearchSuggestions();
        }
    } else if (event.key === 'Escape') {
        hideSearchSuggestions();
    }
}

function performLiveSearch(query) {
    // Live search avec debounce déjà implémenté dans handleSearchInput
    console.log(`Live search: ${query}`);
}

function loadMoreResults() {
    ExploreApp.isLoading = true;
    ExploreApp.currentPage++;
    
    setTimeout(() => {
        // Simuler le chargement de plus de résultats
        const moreResults = generateMockResults(ExploreApp.lastSearchQuery);
        const container = document.getElementById('publicDecksGrid');
        if (container) {
            container.innerHTML += moreResults.map(result => generateDeckCard(result)).join('');
        }
        ExploreApp.isLoading = false;
        initCardInteractions();
    }, 1000);
}

// ===== EXPORT DES FONCTIONS GLOBALES =====
window.ExploreApp = ExploreApp;
window.toggleNotificationCenter = toggleNotificationCenter;
window.importDeck = importDeck;
window.previewDeck = previewDeck;

// ===== NOTIFICATION ACTIONS =====
/**
 * Marquer toutes les notifications comme lues
 */
function markAllNotificationsRead() {
    console.log('🔔 Marking all notifications as read...');
    // TODO: Implémenter l'appel API
    window.notificationService?.success('Toutes les notifications ont été marquées comme lues');
}

/**
 * Ouvrir les paramètres de notifications
 */
function showNotificationSettings() {
    console.log('⚙️ Opening notification settings...');
    // TODO: Ouvrir le modal des paramètres de notifications
    const modal = document.getElementById('notificationSettingsModal');
    if (modal) {
        // Utiliser Bootstrap modal si disponible
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = new window.bootstrap.Modal(modal);
            modalInstance.show();
        } else {
            // Fallback pour Tailwind modals
            modal.style.display = 'block';
            modal.setAttribute('aria-hidden', 'false');
        }
    }
}

/**
 * Ouvrir toutes les notifications dans un modal
 */
function showAllNotifications() {
    console.log('📋 Opening all notifications modal...');
    // TODO: Ouvrir le modal complet des notifications
    const modal = document.getElementById('allNotificationsModal');
    if (modal) {
        // Utiliser Bootstrap modal si disponible
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = new window.bootstrap.Modal(modal);
            modalInstance.show();
        } else {
            // Fallback pour Tailwind modals
            modal.style.display = 'block';
            modal.setAttribute('aria-hidden', 'false');
        }
    }
}

/**
 * Sauvegarder les paramètres de notifications
 */
function saveNotificationSettings() {
    console.log('💾 Saving notification settings...');
    
    // Récupérer les valeurs des paramètres
    const settings = {
        enableNotifications: document.getElementById('enableNotifications')?.checked || false,
        enableSoundNotifications: document.getElementById('enableSoundNotifications')?.checked || false,
        enableBadgeNotifications: document.getElementById('enableBadgeNotifications')?.checked || false,
        notifyNewDecks: document.getElementById('notifyNewDecks')?.checked || false,
        notifyFavoritesUpdates: document.getElementById('notifyFavoritesUpdates')?.checked || false,
        notifyCollectionsActivity: document.getElementById('notifyCollectionsActivity')?.checked || false,
        notifyRecommendations: document.getElementById('notifyRecommendations')?.checked || false,
        notifySystem: document.getElementById('notifySystem')?.checked || false,
        notificationFrequency: document.getElementById('notificationFrequency')?.value || 'daily'
    };
    
    // TODO: Envoyer les paramètres au serveur via API
    console.log('Settings to save:', settings);
    
    // Fermer le modal
    const modal = document.getElementById('notificationSettingsModal');
    if (modal) {
        if (window.bootstrap && window.bootstrap.Modal) {
            const modalInstance = window.bootstrap.Modal.getInstance(modal);
            if (modalInstance) modalInstance.hide();
        } else {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
    }
    
    // Afficher un message de succès
    if (window.notificationService) {
        window.notificationService.success('Paramètres de notifications sauvegardés');
    } else {
        console.log('✅ Notification settings saved successfully');
    }
}

// ===== SIDEBAR MANAGEMENT =====
/**
 * Toggle de la sidebar pour les filtres
 */
function toggleSidebar() {
    const sidebar = document.getElementById('exploreSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar) {
        const isVisible = sidebar.classList.contains('show');
        
        if (isVisible) {
            sidebar.classList.remove('show');
            if (overlay) overlay.style.display = 'none';
        } else {
            sidebar.classList.add('show');
            if (overlay) overlay.style.display = 'block';
        }
    }
}

// ===== NOTIFICATION HANDLERS =====
/**
 * Gestionnaires pour les actions de notification individuelles
 */
document.addEventListener('DOMContentLoaded', function() {
    // Event listeners pour les boutons principaux
    const notificationBtn = document.getElementById('notificationBtn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', toggleNotificationCenter);
    }
    
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    const notificationOverlay = document.getElementById('notificationOverlay');
    if (notificationOverlay) {
        notificationOverlay.addEventListener('click', toggleNotificationCenter);
    }
    
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }
    
    // Event listeners pour les actions de notification
    document.addEventListener('click', function(e) {
        // Boutons d'action des notifications
        if (e.target.classList.contains('notification-action-btn')) {
            const action = e.target.textContent.trim().toLowerCase();
            const notificationItem = e.target.closest('.notification-item');
            const title = notificationItem.querySelector('.notification-title').textContent;
            
            if (action === 'voir') {
                console.log(`👀 Viewing notification: ${title}`);
                // TODO: Naviguer vers le contenu de la notification
            } else if (action === 'ignorer') {
                console.log(`🚫 Ignoring notification: ${title}`);
                // Supprimer visuellement la notification
                notificationItem.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => {
                    notificationItem.remove();
                    // TODO: Mettre à jour les compteurs
                }, 300);
            }
        }
        
        // Gestionnaires pour les boutons avec IDs spécifiques
        if (e.target.id === 'saveNotificationSettingsBtn') {
            saveNotificationSettings();
            e.preventDefault();
        } else if (e.target.id === 'markAllNotificationsReadBtn') {
            markAllNotificationsRead();
            e.preventDefault();
        }
        
        // Gestionnaires pour les actions de notification management par contenu
        const text = e.target.textContent?.trim();
        if (text) {
            if (text.includes('Marquer tout comme lu')) {
                markAllNotificationsRead();
                e.preventDefault();
            } else if (text.includes('Paramètres') && e.target.title === 'Paramètres') {
                showNotificationSettings();
                e.preventDefault();
            } else if (text.includes('Voir toutes les notifications')) {
                showAllNotifications();
                e.preventDefault();
            }
        }
    });
});

// ===== ANIMATION UTILITIES =====
/**
 * Animation de sortie pour les notifications supprimées
 */
const slideOutAnimation = `
@keyframes slideOutRight {
    from {
        opacity: 1;
        transform: translateX(0);
    }
    to {
        opacity: 0;
        transform: translateX(100%);
    }
}
`;

// Injecter l'animation dans le document
if (!document.getElementById('explore-animations')) {
    const style = document.createElement('style');
    style.id = 'explore-animations';
    style.textContent = slideOutAnimation;
    document.head.appendChild(style);
}

// ===== FILTER FUNCTIONS =====
/**
 * Select status filter for Explorer page
 * @param {string} value - Filter value
 * @param {string} text - Display text
 */
function selectStatusFilter(value, text) {
    try {
        console.log(`📊 Explorer status filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('statusFilterText');
        const items = document.querySelectorAll('#statusFilterDropdown .dropdown-item');
        
        if (!textElement) {
            console.warn('⚠️ Status filter text element not found in Explorer');
            return;
        }
        
        textElement.textContent = text;
        
        // Update selected state
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('⚠️ Error updating item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Trigger search update if main explorer module is available
        if (window.explorerMain && typeof window.explorerMain.performSearch === 'function') {
            window.explorerMain.performSearch();
        } else {
            console.log('🔍 Explorer main module not available, filter stored for next search');
        }
        
        console.log('✅ Explorer status filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in Explorer selectStatusFilter:', error.message);
    }
}

/**
 * Select sort filter for Explorer page
 * @param {string} value - Sort value
 * @param {string} text - Display text
 */
function selectSortFilter(value, text) {
    try {
        console.log(`📊 Explorer sort filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('sortFilterText');
        const items = document.querySelectorAll('#sortFilterDropdown .dropdown-item');
        
        if (!textElement) {
            console.warn('⚠️ Sort filter text element not found in Explorer');
            return;
        }
        
        textElement.textContent = text;
        
        // Update selected state
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('⚠️ Error updating sort item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Trigger search update if main explorer module is available
        if (window.explorerMain && typeof window.explorerMain.performSearch === 'function') {
            window.explorerMain.performSearch();
        } else {
            console.log('🔍 Explorer main module not available, filter stored for next search');
        }
        
        console.log('✅ Explorer sort filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in Explorer selectSortFilter:', error.message);
    }
}

/**
 * Select tags filter for Explorer page
 * @param {string} value - Tag value
 * @param {string} text - Display text
 */
function selectTagsFilter(value, text) {
    try {
        console.log(`📊 Explorer tags filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('tagsFilterText');
        const items = document.querySelectorAll('#tagsFilterDropdown .dropdown-item');
        
        if (!textElement) {
            console.warn('⚠️ Tags filter text element not found in Explorer');
            return;
        }
        
        textElement.textContent = text;
        
        // Update selected state
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('⚠️ Error updating tags item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Trigger search update if main explorer module is available
        if (window.explorerMain && typeof window.explorerMain.performSearch === 'function') {
            window.explorerMain.performSearch();
        } else {
            console.log('🔍 Explorer main module not available, filter stored for next search');
        }
        
        console.log('✅ Explorer tags filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in Explorer selectTagsFilter:', error.message);
    }
}

// ===== EXPORTS POUR AUTRES MODULES =====
window.exploreNewModule = {
    toggleNotificationCenter,
    markAllNotificationsRead,
    showNotificationSettings,
    showAllNotifications,
    toggleSidebar,
    selectStatusFilter,
    selectSortFilter,
    selectTagsFilter
};

// Make filter functions globally available for navbar onclick handlers
window.selectStatusFilter = selectStatusFilter;
window.selectSortFilter = selectSortFilter;
window.selectTagsFilter = selectTagsFilter;

console.log('🚀 Explore New JS module loaded successfully');