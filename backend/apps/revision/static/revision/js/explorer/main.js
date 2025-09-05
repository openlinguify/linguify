// Revision Explore Interface Manager
// État global pour l'exploration - version améliorée
let exploreState = {
    publicDecks: [],
    popularDecks: [],
    trendingDecks: [],
    currentPage: 1,
    totalPages: 1,
    totalDecks: 0,
    isLoading: false,
    selectedDeck: null,
    viewMode: 'grid', // 'grid' ou 'list'
    filters: {
        search: '',
        author: '',
        category: '',
        language: '',
        level: '',
        rating: '',
        sortBy: 'created_at',
        minCards: '',
        maxCards: ''
    },
    search: {
        isActive: false,
        suggestions: [],
        history: JSON.parse(localStorage.getItem('linguify_search_history') || '[]'),
        selectedSuggestion: -1,
        isVoiceListening: false,
        voiceRecognition: null,
        advancedSearchVisible: false,
        recentSearches: [],
        quickFilters: []
    },
    favorites: {
        decks: JSON.parse(localStorage.getItem('linguify_favorite_decks') || '[]'),
        isLoading: false
    },
    collections: {
        list: [],
        selected: null,
        isLoading: false,
        deckToAdd: null
    },
    notifications: {
        list: [],
        unreadCount: 0,
        isVisible: false,
        activeFilter: 'all',
        settings: JSON.parse(localStorage.getItem('linguify_notification_settings') || JSON.stringify({
            enabled: true,
            sounds: false,
            badge: true,
            newDecks: true,
            favoritesUpdates: true,
            collectionsActivity: true,
            recommendations: true,
            system: false,
            frequency: 'daily'
        })),
        lastCheck: localStorage.getItem('linguify_last_notification_check') || new Date().toISOString()
    },
    analytics: {
        sessionStart: new Date().toISOString(),
        interactions: [],
        metrics: {
            searchQueries: 0,
            decksViewed: 0,
            decksImported: 0,
            favoritesAdded: 0,
            collectionsCreated: 0,
            filtersApplied: 0,
            timeSpent: 0,
            popularDecksViewed: 0,
            trendingDecksViewed: 0,
            notificationClicks: 0
        },
        heatmap: {
            searchTerms: JSON.parse(localStorage.getItem('linguify_search_heatmap') || '{}'),
            categories: JSON.parse(localStorage.getItem('linguify_category_heatmap') || '{}'),
            authors: JSON.parse(localStorage.getItem('linguify_author_heatmap') || '{}'),
            languages: JSON.parse(localStorage.getItem('linguify_language_heatmap') || '{}')
        },
        performanceMetrics: {
            pageLoadTime: 0,
            apiResponseTimes: [],
            errorCount: 0,
            retryCount: 0
        },
        userBehavior: {
            scrollDepth: 0,
            clickHeatmap: [],
            dwellTime: {},
            exitPoints: [],
            entryPoints: []
        }
    },
    stats: {
        totalDecks: 0,
        totalCards: 0,
        totalAuthors: 0,
        totalDownloads: 0,
        avgRating: 0
    },
    categories: {
        'languages': { name: 'Langues', icon: '🌐', color: 'var(--linguify-primary)' },
        'science': { name: 'Sciences', icon: '🔬', color: 'var(--linguify-success)' },
        'history': { name: 'Histoire', icon: '📚', color: 'var(--linguify-warning)' },
        'math': { name: 'Mathématiques', icon: '🔢', color: 'var(--linguify-accent)' },
        'literature': { name: 'Littérature', icon: '📖', color: 'var(--linguify-secondary)' },
        'medicine': { name: 'Médecine', icon: '⚕️', color: '#e53e3e' },
        'technology': { name: 'Technologie', icon: '💻', color: '#3182ce' },
        'business': { name: 'Business', icon: '💼', color: '#d69e2e' },
        'art': { name: 'Art & Culture', icon: '🎨', color: '#805ad5' },
        'other': { name: 'Autres', icon: '📋', color: '#718096' }
    }
};

// API Service pour les decks publics
const exploreAPI = {
    async getPublicDecks(page = 1, filters = {}) {
        const params = new URLSearchParams({
            page: page,
            ...filters
        });
        
        return await window.apiService.request(`/api/v1/revision/public/?${params}`);
    },
    
    async getPublicDeck(id) {
        return await window.apiService.request(`/api/v1/revision/public/${id}/`);
    },
    
    async getPublicDeckCards(id) {
        return await window.apiService.request(`/api/v1/revision/public/${id}/cards/`);
    },
    
    async clonePublicDeck(id, data = {}) {
        return await window.apiService.request(`/api/v1/revision/public/${id}/clone/`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async getPublicStats() {
        return await window.apiService.request('/api/v1/revision/public/stats/');
    },

    async getTrendingDecks() {
        return await window.apiService.request('/api/v1/revision/public/trending/');
    },

    async getPopularDecks() {
        return await window.apiService.request('/api/v1/revision/public/popular/');
    },

    async rateDeck(deckId, rating) {
        return await window.apiService.request(`/api/v1/revision/public/${deckId}/rate/`, {
            method: 'POST',
            body: JSON.stringify({ rating })
        });
    },

    async getRecommendations(deckId = null) {
        const url = deckId 
            ? `/api/v1/revision/public/recommendations/?based_on=${deckId}`
            : '/api/v1/revision/public/recommendations/';
        return await window.apiService.request(url);
    },

    async searchDecks(query, filters = {}) {
        const params = new URLSearchParams({
            search: query,
            ...filters
        });
        return await window.apiService.request(`/api/v1/revision/public/search/?${params}`);
    },

    async getDeckReviews(deckId, page = 1) {
        return await window.apiService.request(`/api/v1/revision/public/${deckId}/reviews/?page=${page}`);
    },

    async getDeckRatingStats(deckId) {
        return await window.apiService.request(`/api/v1/revision/public/${deckId}/rating-stats/`);
    },

    async getUserRating(deckId) {
        return await window.apiService.request(`/api/v1/revision/public/${deckId}/user-rating/`);
    },

    async getAuthorProfile(userId) {
        return await window.apiService.request(`/api/v1/users/${userId}/profile/`);
    },

    async getAuthorDecks(userId, limit = 5) {
        return await window.apiService.request(`/api/v1/users/${userId}/decks/?limit=${limit}`);
    },

    async markReviewHelpful(reviewId) {
        return await window.apiService.request(`/api/v1/reviews/${reviewId}/helpful/`, {
            method: 'POST'
        });
    },

    async getSearchSuggestions(query, limit = 8) {
        const params = new URLSearchParams({
            q: query,
            limit: limit
        });
        return await window.apiService.request(`/api/v1/revision/public/suggest/?${params}`);
    },

    async getPopularSearchTerms() {
        return await window.apiService.request('/api/v1/revision/public/popular-searches/');
    },

    async logSearchQuery(query, resultCount = 0) {
        return await window.apiService.request('/api/v1/revision/public/log-search/', {
            method: 'POST',
            body: JSON.stringify({ 
                query: query,
                result_count: resultCount,
                timestamp: new Date().toISOString()
            })
        });
    },

    async getAutoComplete(query, types = ['decks', 'authors', 'tags']) {
        const params = new URLSearchParams({
            q: query,
            types: types.join(','),
            limit: 10
        });
        return await window.apiService.request(`/api/v1/revision/public/autocomplete/?${params}`);
    },

    // Favorites API
    async getFavorites() {
        return await window.apiService.request('/api/v1/revision/favorites/');
    },

    async addToFavorites(deckId) {
        return await window.apiService.request('/api/v1/revision/favorites/', {
            method: 'POST',
            body: JSON.stringify({ deck_id: deckId })
        });
    },

    async removeFromFavorites(deckId) {
        return await window.apiService.request(`/api/v1/revision/favorites/${deckId}/`, {
            method: 'DELETE'
        });
    },

    // Collections API
    async getCollections() {
        return await window.apiService.request('/api/v1/revision/collections/');
    },

    async createCollection(data) {
        return await window.apiService.request('/api/v1/revision/collections/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateCollection(collectionId, data) {
        return await window.apiService.request(`/api/v1/revision/collections/${collectionId}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    async deleteCollection(collectionId) {
        return await window.apiService.request(`/api/v1/revision/collections/${collectionId}/`, {
            method: 'DELETE'
        });
    },

    async addDeckToCollection(collectionId, deckId) {
        return await window.apiService.request(`/api/v1/revision/collections/${collectionId}/add-deck/`, {
            method: 'POST',
            body: JSON.stringify({ deck_id: deckId })
        });
    },

    async removeDeckFromCollection(collectionId, deckId) {
        return await window.apiService.request(`/api/v1/revision/collections/${collectionId}/remove-deck/`, {
            method: 'POST',
            body: JSON.stringify({ deck_id: deckId })
        });
    },

    async getCollectionDecks(collectionId) {
        return await window.apiService.request(`/api/v1/revision/collections/${collectionId}/decks/`);
    },

    // Notification API endpoints
    async getNotifications(filters = {}) {
        const params = new URLSearchParams(filters);
        return await window.apiService.request(`/api/v1/notifications/?${params}`);
    },

    async markNotificationRead(notificationId) {
        return await window.apiService.request(`/api/v1/notifications/${notificationId}/read/`, {
            method: 'POST'
        });
    },

    async markAllNotificationsRead() {
        return await window.apiService.request('/api/v1/notifications/mark-all-read/', {
            method: 'POST'
        });
    },

    async getNotificationSettings() {
        return await window.apiService.request('/api/v1/notifications/settings/');
    },

    async updateNotificationSettings(settings) {
        return await window.apiService.request('/api/v1/notifications/settings/', {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
    },

    async dismissNotification(notificationId) {
        return await window.apiService.request(`/api/v1/notifications/${notificationId}/dismiss/`, {
            method: 'POST'
        });
    },

    async getUnreadNotificationCount() {
        return await window.apiService.request('/api/v1/notifications/unread-count/');
    },

    // Analytics API endpoints
    async trackEvent(eventType, eventData) {
        return await window.apiService.request('/api/v1/analytics/events/', {
            method: 'POST',
            body: JSON.stringify({
                event_type: eventType,
                event_data: eventData,
                timestamp: new Date().toISOString()
            })
        });
    },

    async getAnalyticsOverview() {
        return await window.apiService.request('/api/v1/analytics/overview/');
    },

    async getDeckAnalytics(deckId) {
        return await window.apiService.request(`/api/v1/analytics/decks/${deckId}/`);
    },

    async getSearchAnalytics() {
        return await window.apiService.request('/api/v1/analytics/search/');
    },

    async getUserAnalytics() {
        return await window.apiService.request('/api/v1/analytics/user/');
    },

    async getPerformanceMetrics() {
        return await window.apiService.request('/api/v1/analytics/performance/');
    },

    async submitAnalyticsSession(sessionData) {
        return await window.apiService.request('/api/v1/analytics/sessions/', {
            method: 'POST',
            body: JSON.stringify(sessionData)
        });
    }
};

// Interface Management Functions
function showExploreWelcome() {
    const elements = getExploreElements();
    hideAllExploreSections();
    elements.exploreWelcome.style.display = 'block';
    loadPublicStats();
}

function showExploreResults() {
    const elements = getExploreElements();
    hideAllExploreSections();
    elements.exploreResults.style.display = 'block';
    loadPublicDecks();
}

function showPublicDeckDetails(deckId) {
    const elements = getExploreElements();
    hideAllExploreSections();
    elements.publicDeckDetails.style.display = 'block';
    loadPublicDeckDetails(deckId);
    
    // Track deck view analytics
    trackEvent('deck_details_opened', { 
        deckId: deckId,
        viewSource: getViewSource()
    });
}

function hideAllExploreSections() {
    const elements = getExploreElements();
    elements.exploreWelcome.style.display = 'none';
    elements.exploreResults.style.display = 'none';
    elements.publicDeckDetails.style.display = 'none';
}

// Data Loading Functions
async function loadPublicStats() {
    try {
        const stats = await exploreAPI.getPublicStats();
        exploreState.stats = stats;
        updateStatsDisplay();
        console.log('Public stats loaded:', stats);
    } catch (error) {
        console.error('Error loading public stats:', error);
        // Fallback values
        exploreState.stats = {
            totalDecks: 0,
            totalCards: 0,
            totalAuthors: 0
        };
        updateStatsDisplay();
    }
}

async function loadPublicDecks(page = 1) {
    if (exploreState.isLoading) return;
    
    const startTime = Date.now();
    
    try {
        exploreState.isLoading = true;
        showLoading();
        
        const response = await exploreAPI.getPublicDecks(page, exploreState.filters);
        
        exploreState.publicDecks = response.results || [];
        exploreState.currentPage = page;
        exploreState.totalPages = Math.ceil(response.count / 20);
        exploreState.totalDecks = response.count;
        
        hideLoading();
        renderPublicDecks();
        renderPagination();
        updateResultsCount();
        
        // Track analytics
        trackEvent('decks_loaded', {
            page: page,
            totalResults: response.count,
            filters: Object.keys(exploreState.filters).filter(key => exploreState.filters[key]),
            loadTime: Date.now() - startTime
        });
        
    } catch (error) {
        console.error('Error loading public decks:', error);
        hideLoading();
        showError('Erreur lors du chargement des decks publics');
    } finally {
        exploreState.isLoading = false;
    }
}

async function loadPublicDeckDetails(deckId) {
    try {
        showLoading();
        
        const [deck, cards, ratingStats, reviews, authorProfile] = await Promise.all([
            exploreAPI.getPublicDeck(deckId),
            exploreAPI.getPublicDeckCards(deckId),
            exploreAPI.getDeckRatingStats(deckId).catch(() => null),
            exploreAPI.getDeckReviews(deckId, 1).catch(() => ({ results: [] })),
            exploreAPI.getAuthorProfile(deck?.user?.id || 1).catch(() => null)
        ]);
        
        exploreState.selectedDeck = { 
            ...deck, 
            cards,
            ratingStats,
            reviews: reviews.results || [],
            authorProfile 
        };
        
        // Load user's rating if authenticated
        try {
            const userRating = await exploreAPI.getUserRating(deckId);
            exploreState.selectedDeck.userRating = userRating.rating || 0;
        } catch (error) {
            exploreState.selectedDeck.userRating = 0;
        }
        
        hideLoading();
        renderPublicDeckDetails();
        renderDeckRating();
        renderDeckReviews();
        renderAuthorProfile();
        
    } catch (error) {
        console.error('Error loading public deck details:', error);
        hideLoading();
        showError('Erreur lors du chargement des détails du deck');
    }
}

async function loadPopularDecks() {
    try {
        const response = await exploreAPI.getPublicDecks(1, { 
            sort_by: 'popularity',
            page_size: 5 
        });
        
        exploreState.popularDecks = response.results || [];
        renderPopularDecks();
        console.log('Popular decks loaded:', exploreState.popularDecks);
        
    } catch (error) {
        console.error('Error loading popular decks:', error);
        exploreState.popularDecks = [];
        renderPopularDecks();
    }
}

async function loadTrendingDecks() {
    try {
        const response = await exploreAPI.getTrendingDecks();
        exploreState.trendingDecks = response.results || [];
        console.log('Trending decks loaded:', exploreState.trendingDecks);
        
        // If no popular decks, use trending as fallback
        if (exploreState.popularDecks.length === 0) {
            exploreState.popularDecks = exploreState.trendingDecks.slice(0, 5);
            renderPopularDecks();
        }
        
    } catch (error) {
        console.error('Error loading trending decks:', error);
        exploreState.trendingDecks = [];
    }
}

// Rendering Functions
function renderPublicDecks() {
    const elements = getExploreElements();
    const container = elements.publicDecksGrid;
    
    if (exploreState.publicDecks.length === 0) {
        elements.noResults.style.display = 'block';
        container.innerHTML = '';
        return;
    }
    
    elements.noResults.style.display = 'none';
    
    if (exploreState.viewMode === 'grid') {
        container.className = 'row g-4 p-4';
        container.innerHTML = exploreState.publicDecks.map(deck => renderDeckCard(deck)).join('');
    } else {
        container.className = 'deck-list-view p-4';
        container.innerHTML = exploreState.publicDecks.map(deck => renderDeckListItem(deck)).join('');
    }
}

function renderDeckCard(deck) {
    const category = exploreState.categories[deck.category] || exploreState.categories['other'];
    const level = deck.level || 'beginner';
    const rating = deck.rating || 0;
    const ratingStars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    const downloads = deck.downloads || Math.floor(Math.random() * 500) + 50;
    const views = deck.views || Math.floor(Math.random() * 1000) + 100;
    
    const isFavorited = exploreState.favorites.decks.includes(deck.id);
    const inCollections = exploreState.collections.list.filter(col => 
        col.decks && col.decks.some(d => d.id === deck.id)
    );
    const inCollection = inCollections.length > 0;
    
    return `
        <div class="col-md-6 col-lg-4">
            <div class="public-deck-card card h-100" onclick="showPublicDeckDetails(${deck.id})">
                ${deck.category ? `<div class="deck-category-badge" style="background: ${category.color}">
                    ${category.icon} ${category.name}
                </div>` : ''}
                
                <!-- Action buttons -->
                <div class="deck-actions">
                    <button class="deck-action-btn ${isFavorited ? 'favorited' : ''}" 
                            onclick="event.stopPropagation(); toggleFavorite(${deck.id})" 
                            title="${isFavorited ? 'Retirer des favoris' : 'Ajouter aux favoris'}">
                        <i class="bi ${isFavorited ? 'bi-heart-fill' : 'bi-heart'}"></i>
                    </button>
                    <button class="deck-action-btn ${inCollection ? 'in-collection' : ''}" 
                            onclick="event.stopPropagation(); showAddToCollectionModal(${deck.id})" 
                            title="${inCollection ? `Dans ${inCollections.length} collection(s)` : 'Ajouter à une collection'}">
                        <i class="bi ${inCollection ? 'bi-collection-fill' : 'bi-plus-circle'}"></i>
                    </button>
                </div>
                
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-start">
                        <div style="flex: 1;">
                            <h6 class="mb-1 fw-bold">${deck.name}</h6>
                            <small class="text-muted">
                                Par <span class="deck-author">@${deck.user.username}</span>
                            </small>
                            
                            <div class="d-flex align-items-center gap-2 mt-1">
                                <span class="deck-level-indicator deck-level-${level}">
                                    ${getLevelIcon(level)} ${getLevelLabel(level)}
                                </span>
                                ${rating > 0 ? `<div class="rating-stars">
                                    <span class="stars">${ratingStars}</span>
                                    <span class="rating-count">(${deck.rating_count || Math.floor(Math.random() * 50) + 5})</span>
                                </div>` : ''}
                            </div>
                        </div>
                        <span class="deck-stats-badge">
                            ${deck.cards_count || 0} cartes
                        </span>
                    </div>
                </div>
                
                <div class="card-body">
                    <p class="card-text small text-muted mb-3" style="min-height: 60px;">
                        ${deck.description || 'Aucune description disponible'}
                    </p>
                    
                    <div class="engagement-metrics">
                        <div class="metric-item">
                            <i class="bi bi-download"></i>
                            <span class="metric-value">${downloads}</span>
                        </div>
                        <div class="metric-item">
                            <i class="bi bi-eye"></i>
                            <span class="metric-value">${views}</span>
                        </div>
                        <div class="metric-item">
                            <i class="bi bi-calendar3"></i>
                            <span class="metric-value">${formatDate(deck.created_at)}</span>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-end align-items-center mt-3">
                        <button class="btn btn-gradient btn-sm" onclick="event.stopPropagation(); importPublicDeck(${deck.id})">
                            <i class="bi bi-download me-1"></i>
                            Importer
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderDeckListItem(deck) {
    const category = exploreState.categories[deck.category] || exploreState.categories['other'];
    const level = deck.level || 'beginner';
    const rating = deck.rating || 0;
    const ratingStars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    const downloads = deck.downloads || Math.floor(Math.random() * 500) + 50;
    
    return `
        <div class="deck-list-item" onclick="showPublicDeckDetails(${deck.id})">
            <div class="deck-list-avatar">
                ${category.icon}
            </div>
            <div class="deck-list-content">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-1 fw-bold">${deck.name}</h6>
                    <span class="deck-stats-badge">${deck.cards_count || 0} cartes</span>
                </div>
                
                <div class="d-flex align-items-center gap-3 mb-2">
                    <small class="text-muted">Par @${deck.user.username}</small>
                    <span class="deck-level-indicator deck-level-${level}">
                        ${getLevelIcon(level)} ${getLevelLabel(level)}
                    </span>
                    ${rating > 0 ? `<div class="rating-stars">
                        <span class="stars">${ratingStars}</span>
                        <span class="rating-count">(${deck.rating_count || Math.floor(Math.random() * 50) + 5})</span>
                    </div>` : ''}
                </div>
                
                <p class="text-muted small mb-0" style="max-width: 600px;">
                    ${deck.description || 'Aucune description disponible'}
                </p>
            </div>
            <div class="deck-list-actions">
                <button class="btn btn-gradient btn-sm" onclick="event.stopPropagation(); importPublicDeck(${deck.id})">
                    <i class="bi bi-download me-1"></i>
                    Importer
                </button>
                <div class="d-flex gap-3 mt-1">
                    <small class="text-muted">
                        <i class="bi bi-download me-1"></i>${downloads}
                    </small>
                    <small class="text-muted">
                        <i class="bi bi-calendar3 me-1"></i>${formatDate(deck.created_at)}
                    </small>
                </div>
            </div>
        </div>
    `;
}

function renderPublicDeckDetails() {
    const elements = getExploreElements();
    const deck = exploreState.selectedDeck;
    
    if (!deck) return;
    
    elements.publicDeckName.textContent = deck.name;
    elements.publicDeckAuthor.textContent = `Par @${deck.user.username}`;
    elements.publicDeckStats.textContent = `${deck.cards_count || 0} cartes`;
    
    // Rendu des cartes
    const cardsContainer = elements.publicDeckCardsPreview;
    cardsContainer.innerHTML = deck.cards.slice(0, 10).map(card => `
        <div class="card-preview">
            <div class="card-preview-front">${card.front_text}</div>
            <div class="card-preview-back">${card.back_text}</div>
        </div>
    `).join('');
    
    if (deck.cards.length > 10) {
        cardsContainer.innerHTML += `
            <div class="text-center mt-3">
                <small class="text-muted">
                    ... et ${deck.cards.length - 10} autres cartes
                </small>
            </div>
        `;
    }
    
    // Rendu des informations
    const infoContainer = elements.publicDeckInfo;
    infoContainer.innerHTML = `
        <div class="mb-3">
            <strong>Description :</strong>
            <p class="mt-1 text-muted">${deck.description || 'Aucune description'}</p>
        </div>
        <div class="mb-3">
            <strong>Auteur :</strong>
            <p class="mt-1">@${deck.user.username}</p>
        </div>
        <div class="mb-3">
            <strong>Nombre de cartes :</strong>
            <p class="mt-1">${deck.cards_count || 0}</p>
        </div>
        <div class="mb-3">
            <strong>Créé le :</strong>
            <p class="mt-1">${formatDate(deck.created_at)}</p>
        </div>
        <div class="mb-3">
            <strong>Langue :</strong>
            <p class="mt-1">${deck.language || 'Non spécifiée'}</p>
        </div>
    `;
}

function renderPopularDecks() {
    const elements = getExploreElements();
    const container = elements.popularDecks;
    
    if (exploreState.popularDecks.length === 0) {
        container.innerHTML = '<p class="text-muted small">Aucun deck populaire trouvé</p>';
        return;
    }
    
    container.innerHTML = exploreState.popularDecks.map((deck, index) => {
        const category = exploreState.categories[deck.category] || exploreState.categories['other'];
        const trendEmoji = index < 3 ? '🔥' : '📈';
        
        return `
            <div class="popular-deck-item" onclick="showPublicDeckDetails(${deck.id})">
                <div class="popular-deck-header">
                    <div class="popular-deck-title">${deck.name}</div>
                    <div class="popular-deck-trend">${trendEmoji}</div>
                </div>
                <div class="popular-deck-meta">
                    <div class="popular-deck-stats">
                        <span>${category.icon}</span>
                        <span>${deck.cards_count || 0} cartes</span>
                    </div>
                    <div class="popular-deck-author">@${deck.user.username}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Rating & Reviews Rendering Functions
function renderDeckRating() {
    const deck = exploreState.selectedDeck;
    if (!deck) return;
    
    const ratingSummary = document.getElementById('ratingSummary');
    const userRatingStars = document.getElementById('userRatingStars');
    
    // Render user rating stars
    if (userRatingStars) {
        const stars = userRatingStars.querySelectorAll('.rating-star');
        stars.forEach((star, index) => {
            const rating = index + 1;
            star.className = `bi rating-star ${rating <= deck.userRating ? 'bi-star-fill filled' : 'bi-star'}`;
            
            star.addEventListener('click', () => setUserRating(deck.id, rating));
            star.addEventListener('mouseenter', () => highlightStars(rating));
            star.addEventListener('mouseleave', () => highlightStars(deck.userRating));
        });
    }
    
    // Render rating summary
    if (ratingSummary && deck.ratingStats) {
        const stats = deck.ratingStats;
        const avgRating = stats.average_rating || 0;
        const totalRatings = stats.total_ratings || 0;
        
        ratingSummary.innerHTML = `
            <div class="d-flex align-items-center justify-content-between mb-3">
                <div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="h4 mb-0 fw-bold text-linguify-primary">${avgRating.toFixed(1)}</span>
                        <div class="rating-stars">
                            <span class="stars">${'★'.repeat(Math.floor(avgRating))}${'☆'.repeat(5 - Math.floor(avgRating))}</span>
                        </div>
                    </div>
                    <small class="text-muted">${totalRatings} avis</small>
                </div>
            </div>
            
            <div class="rating-breakdown">
                ${[5, 4, 3, 2, 1].map(rating => {
                    const count = stats[`rating_${rating}`] || 0;
                    const percentage = totalRatings ? (count / totalRatings * 100) : 0;
                    
                    return `
                        <div class="rating-row">
                            <span>${rating}★</span>
                            <div class="rating-bar">
                                <div class="rating-bar-fill" style="width: ${percentage}%"></div>
                            </div>
                            <span class="rating-count">${count}</span>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
}

function renderDeckReviews() {
    const deck = exploreState.selectedDeck;
    if (!deck) return;
    
    const reviewsList = document.getElementById('reviewsList');
    if (!reviewsList) return;
    
    const reviews = deck.reviews || [];
    
    if (reviews.length === 0) {
        reviewsList.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-chat-text mb-2" style="font-size: 2rem;"></i>
                <p class="mb-0">Aucun avis pour le moment.</p>
                <small>Soyez le premier à laisser un avis !</small>
            </div>
        `;
        return;
    }
    
    reviewsList.innerHTML = reviews.map(review => {
        const ratingStars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
        const userInitial = review.user.username.charAt(0).toUpperCase();
        
        return `
            <div class="review-item">
                <div class="review-header">
                    <div class="reviewer-avatar">${userInitial}</div>
                    <div class="reviewer-info">
                        <div class="reviewer-name">@${review.user.username}</div>
                        <div class="review-date">${formatDate(review.created_at)}</div>
                    </div>
                    <div class="review-rating">${ratingStars}</div>
                </div>
                
                ${review.comment ? `<div class="review-text">${review.comment}</div>` : ''}
                
                <div class="review-helpful">
                    <button class="helpful-btn" onclick="markReviewHelpful(${review.id})">
                        <i class="bi bi-hand-thumbs-up me-1"></i>
                        Utile
                    </button>
                    <span>${review.helpful_count || 0}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderAuthorProfile() {
    const deck = exploreState.selectedDeck;
    if (!deck || !deck.authorProfile) return;
    
    const authorProfileDiv = document.getElementById('authorProfile');
    if (!authorProfileDiv) return;
    
    const profile = deck.authorProfile;
    const userInitial = profile.username.charAt(0).toUpperCase();
    
    // Mock data for demonstration
    const mockStats = {
        totalDecks: Math.floor(Math.random() * 50) + 5,
        totalDownloads: Math.floor(Math.random() * 5000) + 500,
        avgRating: (Math.random() * 2 + 3).toFixed(1),
        joinDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000)
    };
    
    authorProfileDiv.innerHTML = `
        <div class="author-header">
            <div class="author-avatar-large">${userInitial}</div>
            <div class="author-info">
                <div class="author-username">@${profile.username}</div>
                <div class="author-bio">${profile.bio || 'Créateur passionné de contenu éducatif sur Linguify.'}</div>
                <div class="author-badges">
                    ${profile.is_verified ? '<span class="author-badge">✓ Vérifié</span>' : ''}
                    ${mockStats.totalDecks > 20 ? '<span class="author-badge">🏆 Créateur Pro</span>' : ''}
                    ${mockStats.totalDownloads > 2000 ? '<span class="author-badge">⭐ Populaire</span>' : ''}
                </div>
            </div>
        </div>
        
        <div class="author-stats">
            <div class="author-stat">
                <span class="author-stat-value">${mockStats.totalDecks}</span>
                <span class="author-stat-label">Decks</span>
            </div>
            <div class="author-stat">
                <span class="author-stat-value">${mockStats.totalDownloads}</span>
                <span class="author-stat-label">Téléchargements</span>
            </div>
            <div class="author-stat">
                <span class="author-stat-value">${mockStats.avgRating}★</span>
                <span class="author-stat-label">Note moyenne</span>
            </div>
            <div class="author-stat">
                <span class="author-stat-value">${formatDate(mockStats.joinDate)}</span>
                <span class="author-stat-label">Membre depuis</span>
            </div>
        </div>
        
        <div class="author-recent-decks">
            <h6 class="small fw-bold mb-2">Autres decks de cet auteur</h6>
            <div id="authorOtherDecks">
                <!-- Sera rempli par loadAuthorOtherDecks -->
            </div>
        </div>
    `;
    
    // Load other decks by this author
    loadAuthorOtherDecks(profile.id);
}

async function loadAuthorOtherDecks(userId) {
    try {
        const response = await exploreAPI.getAuthorDecks(userId, 3);
        const decks = response.results || [];
        
        const container = document.getElementById('authorOtherDecks');
        if (!container) return;
        
        if (decks.length === 0) {
            container.innerHTML = '<p class="text-muted small">Aucun autre deck disponible.</p>';
            return;
        }
        
        container.innerHTML = decks.filter(deck => deck.id !== exploreState.selectedDeck.id).map(deck => {
            const category = exploreState.categories[deck.category] || exploreState.categories['other'];
            
            return `
                <div class="recent-deck-item" onclick="showPublicDeckDetails(${deck.id})">
                    <div class="recent-deck-icon">${category.icon}</div>
                    <div class="recent-deck-info">
                        <div class="recent-deck-name">${deck.name}</div>
                        <div class="recent-deck-meta">${deck.cards_count || 0} cartes • ${formatDate(deck.created_at)}</div>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading author other decks:', error);
        const container = document.getElementById('authorOtherDecks');
        if (container) {
            container.innerHTML = '<p class="text-muted small">Erreur lors du chargement.</p>';
        }
    }
}

function renderPagination() {
    const elements = getExploreElements();
    const container = elements.explorePagination;
    
    if (exploreState.totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<div class="pagination-custom">';
    
    // Bouton précédent
    paginationHTML += `
        <button ${exploreState.currentPage === 1 ? 'disabled' : ''} 
                onclick="loadPublicDecks(${exploreState.currentPage - 1})">
            <i class="bi bi-chevron-left"></i>
        </button>
    `;
    
    // Numéros de pages
    const startPage = Math.max(1, exploreState.currentPage - 2);
    const endPage = Math.min(exploreState.totalPages, exploreState.currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <button class="${i === exploreState.currentPage ? 'active' : ''}" 
                    onclick="loadPublicDecks(${i})">
                ${i}
            </button>
        `;
    }
    
    // Bouton suivant
    paginationHTML += `
        <button ${exploreState.currentPage === exploreState.totalPages ? 'disabled' : ''} 
                onclick="loadPublicDecks(${exploreState.currentPage + 1})">
            <i class="bi bi-chevron-right"></i>
        </button>
    `;
    
    paginationHTML += '</div>';
    container.innerHTML = paginationHTML;
}

// Filter Functions
function applyFilters() {
    exploreState.currentPage = 1;
    loadPublicDecks();
}

function clearFilters() {
    const elements = getExploreElements();
    
    exploreState.filters = {
        search: '',
        author: '',
        category: '',
        language: '',
        level: '',
        rating: '',
        sortBy: 'created_at',
        minCards: '',
        maxCards: ''
    };
    
    if (elements.exploreSearchInput) elements.exploreSearchInput.value = '';
    if (elements.authorFilter) elements.authorFilter.value = '';
    if (elements.categoryFilter) elements.categoryFilter.value = '';
    if (elements.languageFilter) elements.languageFilter.value = '';
    if (elements.levelFilter) elements.levelFilter.value = '';
    if (elements.ratingFilter) elements.ratingFilter.value = '';
    if (elements.sortByFilter) elements.sortByFilter.value = 'created_at';
    if (elements.minCards) elements.minCards.value = '';
    if (elements.maxCards) elements.maxCards.value = '';
    
    applyFilters();
}

// Import Functions
async function importPublicDeck(deckId) {
    try {
        const deck = await exploreAPI.getPublicDeck(deckId);
        
        const elements = getExploreElements();
        elements.importDeckName.value = `${deck.name} (Copie)`;
        
        const modal = new bootstrap.Modal(elements.importModal);
        modal.show();
        
        // Stocker l'ID du deck à importer
        exploreState.deckToImport = deckId;
        
    } catch (error) {
        console.error('Error preparing import:', error);
        window.notificationService.error('Erreur lors de la préparation de l\'import');
    }
}

async function confirmImportDeck() {
    if (!exploreState.deckToImport) return;
    
    try {
        const elements = getExploreElements();
        const customName = elements.importDeckName.value.trim();
        
        const importData = customName ? { name: customName } : {};
        
        await exploreAPI.clonePublicDeck(exploreState.deckToImport, importData);
        
        window.notificationService.success('Deck importé avec succès dans votre collection !');
        
        // Fermer la modal
        const modal = bootstrap.Modal.getInstance(elements.importModal);
        modal.hide();
        
        // Nettoyer
        exploreState.deckToImport = null;
        elements.importDeckName.value = '';
        
    } catch (error) {
        console.error('Error importing deck:', error);
        window.notificationService.error('Erreur lors de l\'import du deck');
    }
}

// UI Helper Functions
function showLoading() {
    const elements = getExploreElements();
    elements.exploreLoading.style.display = 'block';
}

function hideLoading() {
    const elements = getExploreElements();
    elements.exploreLoading.style.display = 'none';
}

function showError(message) {
    window.notificationService.error(message);
}

function updateStatsDisplay() {
    const elements = getExploreElements();
    elements.totalPublicDecks.textContent = exploreState.stats.totalDecks || 0;
    elements.totalPublicCards.textContent = exploreState.stats.totalCards || 0;
    elements.totalAuthors.textContent = exploreState.stats.totalAuthors || 0;
}

function updateResultsCount() {
    const elements = getExploreElements();
    elements.resultsCount.textContent = exploreState.totalDecks;
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function getLevelIcon(level) {
    const icons = {
        'beginner': '🟢',
        'intermediate': '🟡', 
        'advanced': '🔴',
        'expert': '⚫'
    };
    return icons[level] || '🟢';
}

function getLevelLabel(level) {
    const labels = {
        'beginner': 'Débutant',
        'intermediate': 'Intermédiaire',
        'advanced': 'Avancé', 
        'expert': 'Expert'
    };
    return labels[level] || 'Débutant';
}

// View Mode Functions
function setViewMode(mode) {
    exploreState.viewMode = mode;
    
    // Update UI buttons
    const gridBtn = document.getElementById('gridView');
    const listBtn = document.getElementById('listView');
    
    if (gridBtn && listBtn) {
        gridBtn.checked = (mode === 'grid');
        listBtn.checked = (mode === 'list');
    }
    
    // Re-render decks
    renderPublicDecks();
}

// Rating Functions
async function setUserRating(deckId, rating) {
    try {
        await exploreAPI.rateDeck(deckId, rating);
        exploreState.selectedDeck.userRating = rating;
        
        // Update the visual stars
        highlightStars(rating);
        
        // Show success message
        window.notificationService?.success(`Vous avez attribué ${rating} étoile${rating > 1 ? 's' : ''} à ce deck !`);
        
        // Optionally reload rating stats
        const ratingStats = await exploreAPI.getDeckRatingStats(deckId);
        exploreState.selectedDeck.ratingStats = ratingStats;
        renderDeckRating();
        
    } catch (error) {
        console.error('Error rating deck:', error);
        window.notificationService?.error('Erreur lors de l\'attribution de la note');
    }
}

function highlightStars(rating) {
    const stars = document.querySelectorAll('#userRatingStars .rating-star');
    stars.forEach((star, index) => {
        const starRating = index + 1;
        if (starRating <= rating) {
            star.classList.remove('bi-star');
            star.classList.add('bi-star-fill', 'filled');
        } else {
            star.classList.remove('bi-star-fill', 'filled');
            star.classList.add('bi-star');
        }
    });
}

// Review Functions
async function markReviewHelpful(reviewId) {
    try {
        await exploreAPI.markReviewHelpful(reviewId);
        
        // Update the helpful count in UI
        const helpfulSpan = document.querySelector(`[onclick="markReviewHelpful(${reviewId})"]`).parentNode.querySelector('span');
        const currentCount = parseInt(helpfulSpan.textContent) || 0;
        helpfulSpan.textContent = currentCount + 1;
        
        // Disable the button
        const button = document.querySelector(`[onclick="markReviewHelpful(${reviewId})"]`);
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hand-thumbs-up-fill me-1"></i>Merci !';
        button.style.color = 'var(--linguify-success)';
        
        window.notificationService?.success('Merci pour votre retour !');
        
    } catch (error) {
        console.error('Error marking review helpful:', error);
        window.notificationService?.error('Erreur lors du vote');
    }
}

async function loadMoreReviews() {
    const deck = exploreState.selectedDeck;
    if (!deck) return;
    
    try {
        const nextPage = Math.floor(deck.reviews.length / 10) + 1;
        const response = await exploreAPI.getDeckReviews(deck.id, nextPage);
        const newReviews = response.results || [];
        
        if (newReviews.length === 0) {
            const button = document.getElementById('loadMoreReviews');
            button.style.display = 'none';
            return;
        }
        
        // Append new reviews
        deck.reviews = [...deck.reviews, ...newReviews];
        renderDeckReviews();
        
    } catch (error) {
        console.error('Error loading more reviews:', error);
        window.notificationService?.error('Erreur lors du chargement des avis');
    }
}

// ===== ADVANCED SEARCH SYSTEM =====

// Search Initialization
function initializeAdvancedSearch() {
    const searchInput = document.getElementById('exploreSearchInput');
    const voiceBtn = document.getElementById('voiceSearchBtn');
    const advancedBtn = document.getElementById('advancedSearchToggle');
    
    if (!searchInput) return;
    
    // Initialize search state
    exploreState.search.quickFilters = [];
    
    // Setup event listeners
    setupSearchEventListeners(searchInput, voiceBtn, advancedBtn);
    
    // Initialize voice search if available
    initializeVoiceSearch();
    
    // Load and render search history
    renderSearchHistory();
    
    // Initialize quick filters
    initializeQuickFilters();
    
    // Load popular search terms
    loadPopularSearchTerms();
}

function setupSearchEventListeners(searchInput, voiceBtn, advancedBtn) {
    // Main search input
    searchInput.addEventListener('input', debounce(handleSearchInput, 150));
    searchInput.addEventListener('focus', handleSearchFocus);
    searchInput.addEventListener('blur', handleSearchBlur);
    searchInput.addEventListener('keydown', handleSearchKeydown);
    
    // Voice search button
    voiceBtn?.addEventListener('click', toggleVoiceSearch);
    
    // Advanced search toggle
    advancedBtn?.addEventListener('click', toggleAdvancedSearch);
    
    // Search history clear button
    const clearHistoryBtn = document.getElementById('clearSearchHistory');
    clearHistoryBtn?.addEventListener('click', clearSearchHistory);
    
    // Sidebar toggle button
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    sidebarToggleBtn?.addEventListener('click', toggleSidebar);
    
    // Initialize sidebar state on desktop
    if (window.innerWidth >= 769) {
        const sidebar = document.getElementById('exploreSidebar');
        const toggleBtn = document.getElementById('toggleSidebar');
        if (sidebar && sidebar.classList.contains('show') && toggleBtn) {
            toggleBtn.classList.add('active');
        }
    }
    
    // Global click handler for closing dropdowns
    document.addEventListener('click', handleGlobalClick);
}

async function handleSearchInput(event) {
    const query = event.target.value.trim();
    exploreState.filters.search = query;
    
    if (query.length >= 2) {
        exploreState.search.isActive = true;
        await loadSearchSuggestions(query);
        showSearchSuggestions();
    } else {
        hideSearchSuggestions();
        if (query.length === 0) {
            showSearchHistory();
        }
    }
    
    // Update search with debounced filter application
    if (query.length >= 3 || query.length === 0) {
        applyFilters();
    }
}

function handleSearchFocus(event) {
    const query = event.target.value.trim();
    
    if (query.length >= 2) {
        showSearchSuggestions();
    } else {
        showSearchHistory();
    }
}

function handleSearchBlur(event) {
    // Delayed to allow clicks on suggestions
    setTimeout(() => {
        hideSearchSuggestions();
        hideSearchHistory();
    }, 150);
}

function handleSearchKeydown(event) {
    const suggestionsDiv = document.getElementById('searchSuggestions');
    const suggestions = suggestionsDiv?.querySelectorAll('.suggestion-item') || [];
    
    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            exploreState.search.selectedSuggestion = Math.min(
                exploreState.search.selectedSuggestion + 1,
                suggestions.length - 1
            );
            highlightSuggestion();
            break;
            
        case 'ArrowUp':
            event.preventDefault();
            exploreState.search.selectedSuggestion = Math.max(
                exploreState.search.selectedSuggestion - 1,
                -1
            );
            highlightSuggestion();
            break;
            
        case 'Enter':
            event.preventDefault();
            if (exploreState.search.selectedSuggestion >= 0 && suggestions[exploreState.search.selectedSuggestion]) {
                selectSuggestion(suggestions[exploreState.search.selectedSuggestion]);
            } else {
                performSearch(event.target.value);
            }
            break;
            
        case 'Escape':
            hideSearchSuggestions();
            hideSearchHistory();
            event.target.blur();
            break;
    }
}

function handleGlobalClick(event) {
    const searchContainer = document.querySelector('.search-input-wrapper');
    if (!searchContainer?.contains(event.target)) {
        hideSearchSuggestions();
        hideSearchHistory();
    }
}

// Search Suggestions
async function loadSearchSuggestions(query) {
    try {
        const response = await exploreAPI.getAutoComplete(query);
        exploreState.search.suggestions = response.results || [];
    } catch (error) {
        console.error('Error loading search suggestions:', error);
        exploreState.search.suggestions = generateFallbackSuggestions(query);
    }
}

function generateFallbackSuggestions(query) {
    // Generate smart fallback suggestions based on query
    const suggestions = [];
    const lowerQuery = query.toLowerCase();
    
    // Category suggestions
    Object.entries(exploreState.categories).forEach(([key, category]) => {
        if (category.name.toLowerCase().includes(lowerQuery) || key.includes(lowerQuery)) {
            suggestions.push({
                type: 'category',
                title: category.name,
                icon: category.icon,
                filter: { category: key },
                meta: 'Catégorie'
            });
        }
    });
    
    // Mock deck suggestions
    const deckSuggestions = [
        { title: `Anglais ${query}`, cards: 150, author: 'Sarah M.', rating: 4.5 },
        { title: `${query} pour débutants`, cards: 80, author: 'Pierre L.', rating: 4.2 },
        { title: `Maîtrise du ${query}`, cards: 200, author: 'Marie D.', rating: 4.8 }
    ].filter(deck => deck.title.toLowerCase().includes(lowerQuery));
    
    deckSuggestions.forEach(deck => {
        suggestions.push({
            type: 'deck',
            title: deck.title,
            icon: '📚',
            meta: `${deck.cards} cartes • ${deck.author} • ${deck.rating}⭐`,
            action: () => performSearch(deck.title)
        });
    });
    
    return suggestions.slice(0, 8);
}

function showSearchSuggestions() {
    const suggestionsDiv = document.getElementById('searchSuggestions');
    if (!suggestionsDiv || exploreState.search.suggestions.length === 0) return;
    
    hideSearchHistory();
    
    const groupedSuggestions = groupSuggestions(exploreState.search.suggestions);
    let suggestionsHTML = '';
    
    Object.entries(groupedSuggestions).forEach(([type, items]) => {
        if (items.length === 0) return;
        
        const typeLabels = {
            'decks': 'Decks',
            'authors': 'Auteurs',
            'categories': 'Catégories',
            'tags': 'Tags',
            'recent': 'Suggestions'
        };
        
        suggestionsHTML += `
            <div class="suggestion-group">
                <div class="suggestion-header">${typeLabels[type] || type}</div>
                ${items.map(item => renderSuggestionItem(item)).join('')}
            </div>
        `;
    });
    
    suggestionsDiv.innerHTML = suggestionsHTML;
    suggestionsDiv.style.display = 'block';
    
    // Add click listeners
    suggestionsDiv.querySelectorAll('.suggestion-item').forEach((item, index) => {
        item.addEventListener('click', () => selectSuggestion(item));
    });
}

function groupSuggestions(suggestions) {
    const grouped = {
        decks: [],
        authors: [],
        categories: [],
        tags: [],
        recent: []
    };
    
    suggestions.forEach(suggestion => {
        const type = suggestion.type || 'recent';
        if (grouped[type]) {
            grouped[type].push(suggestion);
        } else {
            grouped.recent.push(suggestion);
        }
    });
    
    return grouped;
}

function renderSuggestionItem(item) {
    return `
        <div class="suggestion-item" data-suggestion='${JSON.stringify(item)}'>
            <div class="suggestion-icon">${item.icon || '🔍'}</div>
            <div class="suggestion-content">
                <div class="suggestion-title">${item.title}</div>
                <div class="suggestion-meta">${item.meta || ''}</div>
            </div>
            ${item.stats ? `
                <div class="suggestion-stats">
                    ${item.stats.map(stat => `<span>${stat}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

function selectSuggestion(suggestionElement) {
    const suggestionData = JSON.parse(suggestionElement.getAttribute('data-suggestion'));
    const searchInput = document.getElementById('exploreSearchInput');
    
    if (suggestionData.filter) {
        // Apply filter
        Object.assign(exploreState.filters, suggestionData.filter);
        addQuickFilter(suggestionData);
        searchInput.value = '';
        exploreState.filters.search = '';
    } else if (suggestionData.action) {
        // Execute custom action
        suggestionData.action();
    } else {
        // Use as search term
        searchInput.value = suggestionData.title;
        exploreState.filters.search = suggestionData.title;
        performSearch(suggestionData.title);
    }
    
    hideSearchSuggestions();
    applyFilters();
}

function highlightSuggestion() {
    const suggestions = document.querySelectorAll('.suggestion-item');
    suggestions.forEach((item, index) => {
        item.classList.toggle('highlighted', index === exploreState.search.selectedSuggestion);
    });
}

function hideSearchSuggestions() {
    const suggestionsDiv = document.getElementById('searchSuggestions');
    if (suggestionsDiv) {
        suggestionsDiv.style.display = 'none';
    }
    exploreState.search.selectedSuggestion = -1;
}

// Search History
function showSearchHistory() {
    if (exploreState.search.history.length === 0) return;
    
    const historyDiv = document.getElementById('searchHistory');
    if (!historyDiv) return;
    
    hideSearchSuggestions();
    
    const historyHTML = exploreState.search.history.map((item, index) => `
        <div class="history-item" data-query="${item.query}">
            <i class="bi bi-clock"></i>
            <span class="history-text">${item.query}</span>
            <span class="small text-muted">${item.resultCount || 0} résultats</span>
            <i class="bi bi-x history-remove" data-index="${index}"></i>
        </div>
    `).join('');
    
    historyDiv.querySelector('.history-items').innerHTML = historyHTML;
    historyDiv.style.display = 'block';
    
    // Add event listeners
    historyDiv.querySelectorAll('.history-item').forEach(item => {
        const query = item.getAttribute('data-query');
        item.addEventListener('click', (e) => {
            if (!e.target.classList.contains('history-remove')) {
                performSearch(query);
            }
        });
    });
    
    historyDiv.querySelectorAll('.history-remove').forEach(removeBtn => {
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(e.target.getAttribute('data-index'));
            removeFromSearchHistory(index);
        });
    });
}

function hideSearchHistory() {
    const historyDiv = document.getElementById('searchHistory');
    if (historyDiv) {
        historyDiv.style.display = 'none';
    }
}

function addToSearchHistory(query, resultCount = 0) {
    if (!query.trim()) return;
    
    // Remove if already exists
    exploreState.search.history = exploreState.search.history.filter(item => item.query !== query);
    
    // Add to beginning
    exploreState.search.history.unshift({
        query: query,
        resultCount: resultCount,
        timestamp: Date.now()
    });
    
    // Keep only last 10
    exploreState.search.history = exploreState.search.history.slice(0, 10);
    
    // Save to localStorage
    localStorage.setItem('linguify_search_history', JSON.stringify(exploreState.search.history));
}

function removeFromSearchHistory(index) {
    exploreState.search.history.splice(index, 1);
    localStorage.setItem('linguify_search_history', JSON.stringify(exploreState.search.history));
    renderSearchHistory();
}

function clearSearchHistory() {
    exploreState.search.history = [];
    localStorage.removeItem('linguify_search_history');
    hideSearchHistory();
}

function renderSearchHistory() {
    // Called during initialization to set up history display
    if (exploreState.search.history.length > 0) {
        // History will be shown on focus
    }
}

// Quick Filters
function initializeQuickFilters() {
    const quickFiltersDiv = document.getElementById('quickFilters');
    if (!quickFiltersDiv) return;
    
    // Clear default chips initially
    quickFiltersDiv.innerHTML = '';
    
    // Add event delegation for filter removal
    quickFiltersDiv.addEventListener('click', handleQuickFilterClick);
}

function handleQuickFilterClick(event) {
    if (event.target.classList.contains('filter-remove')) {
        const chip = event.target.closest('.filter-chip');
        if (chip) {
            removeQuickFilter(chip);
        }
    }
}

function addQuickFilter(filterData) {
    if (!filterData.filter) return;
    
    const quickFiltersDiv = document.getElementById('quickFilters');
    if (!quickFiltersDiv) return;
    
    // Check if filter already exists
    const existingChip = quickFiltersDiv.querySelector(`[data-filter="${Object.keys(filterData.filter)[0]}"]`);
    if (existingChip) {
        existingChip.remove();
    }
    
    const filterKey = Object.keys(filterData.filter)[0];
    const filterValue = Object.values(filterData.filter)[0];
    
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    chip.setAttribute('data-filter', filterKey);
    chip.setAttribute('data-value', filterValue);
    chip.innerHTML = `
        ${filterData.icon || '🔍'} ${filterData.title}
        <i class="bi bi-x-circle filter-remove"></i>
    `;
    
    quickFiltersDiv.appendChild(chip);
    exploreState.search.quickFilters.push(filterData);
}

function removeQuickFilter(chipElement) {
    const filterKey = chipElement.getAttribute('data-filter');
    const filterValue = chipElement.getAttribute('data-value');
    
    // Remove from state
    if (exploreState.filters[filterKey] === filterValue) {
        exploreState.filters[filterKey] = '';
    }
    
    // Remove from quick filters array
    exploreState.search.quickFilters = exploreState.search.quickFilters.filter(
        filter => !(filter.filter && filter.filter[filterKey] === filterValue)
    );
    
    // Remove element with animation
    chipElement.style.animation = 'chipSlideOut 0.3s ease forwards';
    setTimeout(() => {
        chipElement.remove();
        applyFilters();
    }, 300);
}

// Voice Search
function initializeVoiceSearch() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        const voiceBtn = document.getElementById('voiceSearchBtn');
        if (voiceBtn) {
            voiceBtn.style.display = 'none';
        }
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    exploreState.search.voiceRecognition = new SpeechRecognition();
    
    exploreState.search.voiceRecognition.lang = 'fr-FR';
    exploreState.search.voiceRecognition.interimResults = true;
    exploreState.search.voiceRecognition.maxAlternatives = 1;
    
    exploreState.search.voiceRecognition.onstart = handleVoiceStart;
    exploreState.search.voiceRecognition.onresult = handleVoiceResult;
    exploreState.search.voiceRecognition.onerror = handleVoiceError;
    exploreState.search.voiceRecognition.onend = handleVoiceEnd;
}

function toggleVoiceSearch() {
    if (!exploreState.search.voiceRecognition) {
        window.notificationService?.error('La recherche vocale n\'est pas supportée par votre navigateur');
        return;
    }
    
    if (exploreState.search.isVoiceListening) {
        stopVoiceSearch();
    } else {
        startVoiceSearch();
    }
}

function startVoiceSearch() {
    exploreState.search.isVoiceListening = true;
    exploreState.search.voiceRecognition.start();
    
    const voiceBtn = document.getElementById('voiceSearchBtn');
    voiceBtn.classList.add('recording');
    voiceBtn.innerHTML = '<i class="bi bi-mic-fill"></i>';
    
    // Add voice animation
    const searchActions = document.querySelector('.search-actions');
    const animation = document.createElement('div');
    animation.className = 'voice-animation';
    animation.innerHTML = '<div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>';
    searchActions.appendChild(animation);
}

function stopVoiceSearch() {
    if (exploreState.search.voiceRecognition && exploreState.search.isVoiceListening) {
        exploreState.search.voiceRecognition.stop();
    }
}

function handleVoiceStart() {
    window.notificationService?.info('🎤 Parlez maintenant...');
}

function handleVoiceResult(event) {
    const transcript = event.results[event.results.length - 1][0].transcript;
    const searchInput = document.getElementById('exploreSearchInput');
    
    if (event.results[event.results.length - 1].isFinal) {
        searchInput.value = transcript;
        exploreState.filters.search = transcript;
        performSearch(transcript);
        stopVoiceSearch();
    } else {
        // Show interim results
        searchInput.placeholder = `Écoute: "${transcript}"...`;
    }
}

function handleVoiceError(event) {
    console.error('Voice recognition error:', event.error);
    let message = 'Erreur de reconnaissance vocale';
    
    switch (event.error) {
        case 'network':
            message = 'Problème de connexion réseau';
            break;
        case 'not-allowed':
            message = 'Accès au microphone refusé';
            break;
        case 'no-speech':
            message = 'Aucune parole détectée';
            break;
    }
    
    window.notificationService?.error(message);
    stopVoiceSearch();
}

function handleVoiceEnd() {
    exploreState.search.isVoiceListening = false;
    
    const voiceBtn = document.getElementById('voiceSearchBtn');
    voiceBtn.classList.remove('recording');
    voiceBtn.innerHTML = '<i class="bi bi-mic"></i>';
    
    // Remove voice animation
    const animation = document.querySelector('.voice-animation');
    if (animation) {
        animation.remove();
    }
    
    // Reset placeholder
    const searchInput = document.getElementById('exploreSearchInput');
    searchInput.placeholder = 'Rechercher des decks par titre, description, tags...';
}

// Advanced Search
function toggleAdvancedSearch() {
    exploreState.search.advancedSearchVisible = !exploreState.search.advancedSearchVisible;
    
    if (exploreState.search.advancedSearchVisible) {
        showAdvancedSearchPanel();
    } else {
        hideAdvancedSearchPanel();
    }
}

function showAdvancedSearchPanel() {
    const container = document.querySelector('.advanced-search-container');
    let panel = container.querySelector('.advanced-search-panel');
    
    if (!panel) {
        panel = document.createElement('div');
        panel.className = 'advanced-search-panel';
        panel.innerHTML = `
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small">Recherche exacte</label>
                    <input type="text" class="form-control form-control-sm" id="exactSearch" placeholder='Ex: "vocabulaire anglais"'>
                </div>
                <div class="col-md-6">
                    <label class="form-label small">Exclure les mots</label>
                    <input type="text" class="form-control form-control-sm" id="excludeWords" placeholder="Ex: -débutant -facile">
                </div>
                <div class="col-md-6">
                    <label class="form-label small">Nombre minimum de cartes</label>
                    <input type="number" class="form-control form-control-sm" id="minCardsAdvanced" min="1" placeholder="Ex: 50">
                </div>
                <div class="col-md-6">
                    <label class="form-label small">Créé dans les derniers</label>
                    <select class="form-select form-select-sm" id="dateRange">
                        <option value="">Toute période</option>
                        <option value="7">7 jours</option>
                        <option value="30">30 jours</option>
                        <option value="90">3 mois</option>
                        <option value="365">1 an</option>
                    </select>
                </div>
            </div>
            
            <div class="search-operators mt-3">
                <span class="small text-muted me-2">Opérateurs:</span>
                <div class="operator-chip" data-op='"text"'>Recherche exacte</div>
                <div class="operator-chip" data-op='-word'>Exclure</div>
                <div class="operator-chip" data-op='word OR word'>OU logique</div>
                <div class="operator-chip" data-op='word AND word'>ET logique</div>
            </div>
            
            <div class="text-end mt-3">
                <button class="btn btn-outline-secondary btn-sm me-2" onclick="resetAdvancedSearch()">
                    <i class="bi bi-arrow-clockwise me-1"></i>Réinitialiser
                </button>
                <button class="btn btn-gradient btn-sm" onclick="applyAdvancedSearch()">
                    <i class="bi bi-search me-1"></i>Rechercher
                </button>
            </div>
        `;
        
        container.appendChild(panel);
        
        // Add event listeners for operators
        panel.querySelectorAll('.operator-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const op = chip.getAttribute('data-op');
                const searchInput = document.getElementById('exploreSearchInput');
                const currentValue = searchInput.value;
                searchInput.value = currentValue ? `${currentValue} ${op}` : op;
                searchInput.focus();
            });
        });
    }
    
    panel.style.display = 'block';
    
    const advancedBtn = document.getElementById('advancedSearchToggle');
    advancedBtn.classList.add('active');
}

function hideAdvancedSearchPanel() {
    const panel = document.querySelector('.advanced-search-panel');
    if (panel) {
        panel.style.display = 'none';
    }
    
    const advancedBtn = document.getElementById('advancedSearchToggle');
    advancedBtn.classList.remove('active');
}

// Sidebar toggle function removed - now handled by inline onclick in navbar

function applyAdvancedSearch() {
    const exactSearch = document.getElementById('exactSearch')?.value || '';
    const excludeWords = document.getElementById('excludeWords')?.value || '';
    const minCards = document.getElementById('minCardsAdvanced')?.value || '';
    const dateRange = document.getElementById('dateRange')?.value || '';
    
    let searchQuery = exactSearch;
    if (excludeWords) {
        searchQuery += ` ${excludeWords}`;
    }
    
    if (minCards) {
        exploreState.filters.minCards = minCards;
    }
    
    if (dateRange) {
        // Add date filter logic
        const dateFilter = new Date();
        dateFilter.setDate(dateFilter.getDate() - parseInt(dateRange));
        exploreState.filters.dateAfter = dateFilter.toISOString().split('T')[0];
    }
    
    const searchInput = document.getElementById('exploreSearchInput');
    searchInput.value = searchQuery;
    exploreState.filters.search = searchQuery;
    
    performSearch(searchQuery);
    hideAdvancedSearchPanel();
}

function resetAdvancedSearch() {
    document.getElementById('exactSearch').value = '';
    document.getElementById('excludeWords').value = '';
    document.getElementById('minCardsAdvanced').value = '';
    document.getElementById('dateRange').value = '';
    
    const searchInput = document.getElementById('exploreSearchInput');
    searchInput.value = '';
    exploreState.filters.search = '';
    exploreState.filters.minCards = '';
    exploreState.filters.dateAfter = '';
    
    applyFilters();
}

// Main Search Function
async function performSearch(query) {
    if (!query.trim()) return;
    
    // Add to search history
    addToSearchHistory(query);
    
    // Log search query
    try {
        await exploreAPI.logSearchQuery(query, exploreState.totalDecks);
    } catch (error) {
        console.error('Error logging search query:', error);
    }
    
    // Update filters and apply
    exploreState.filters.search = query;
    applyFilters();
    
    // Hide search dropdowns
    hideSearchSuggestions();
    hideSearchHistory();
    
    window.notificationService?.info(`🔍 Recherche: "${query}"`);
}

// Popular Search Terms
async function loadPopularSearchTerms() {
    try {
        const response = await exploreAPI.getPopularSearchTerms();
        exploreState.search.popularTerms = response.results || [];
    } catch (error) {
        console.error('Error loading popular search terms:', error);
        exploreState.search.popularTerms = [];
    }
}

// ===== FAVORITES & COLLECTIONS SYSTEM =====

// Favorites Management
async function loadFavorites() {
    try {
        exploreState.favorites.isLoading = true;
        const response = await exploreAPI.getFavorites();
        exploreState.favorites.decks = response.results?.map(fav => fav.deck.id) || [];
        localStorage.setItem('linguify_favorite_decks', JSON.stringify(exploreState.favorites.decks));
        renderFavorites();
        updateFavoritesCount();
    } catch (error) {
        console.error('Error loading favorites:', error);
        // Use cached favorites from localStorage
        renderFavorites();
    } finally {
        exploreState.favorites.isLoading = false;
    }
}

async function toggleFavorite(deckId) {
    const isFavorited = exploreState.favorites.decks.includes(deckId);
    const btn = document.querySelector(`[onclick*="toggleFavorite(${deckId})"]`);
    
    // Optimistic update
    if (isFavorited) {
        exploreState.favorites.decks = exploreState.favorites.decks.filter(id => id !== deckId);
        btn.classList.remove('favorited');
        btn.querySelector('i').className = 'bi bi-heart';
        btn.title = 'Ajouter aux favoris';
    } else {
        exploreState.favorites.decks.push(deckId);
        btn.classList.add('favorited', 'animate-favorite');
        btn.querySelector('i').className = 'bi bi-heart-fill';
        btn.title = 'Retirer des favoris';
        
        // Remove animation class after animation
        setTimeout(() => btn.classList.remove('animate-favorite'), 300);
    }
    
    // Update localStorage immediately
    localStorage.setItem('linguify_favorite_decks', JSON.stringify(exploreState.favorites.decks));
    
    try {
        // Send to server
        if (isFavorited) {
            await exploreAPI.removeFromFavorites(deckId);
            window.notificationService?.success('Retiré des favoris');
        } else {
            await exploreAPI.addToFavorites(deckId);
            window.notificationService?.success('Ajouté aux favoris ❤️');
        }
        
        renderFavorites();
        updateFavoritesCount();
        
    } catch (error) {
        console.error('Error toggling favorite:', error);
        
        // Revert optimistic update on error
        if (isFavorited) {
            exploreState.favorites.decks.push(deckId);
            btn.classList.add('favorited');
            btn.querySelector('i').className = 'bi bi-heart-fill';
            btn.title = 'Retirer des favoris';
        } else {
            exploreState.favorites.decks = exploreState.favorites.decks.filter(id => id !== deckId);
            btn.classList.remove('favorited');
            btn.querySelector('i').className = 'bi bi-heart';
            btn.title = 'Ajouter aux favoris';
        }
        
        localStorage.setItem('linguify_favorite_decks', JSON.stringify(exploreState.favorites.decks));
        window.notificationService?.error('Erreur lors de la mise à jour des favoris');
    }
}

function renderFavorites() {
    const favoritesContainer = document.getElementById('favoriteDecks');
    if (!favoritesContainer) return;
    
    if (exploreState.favorites.decks.length === 0) {
        favoritesContainer.innerHTML = `
            <div class="empty-favorites">
                <i class="bi bi-heart"></i>
                <p>Aucun favori</p>
            </div>
        `;
        return;
    }
    
    // Create mock favorite decks for demo (in real app, would fetch from API)
    const favoriteDecks = exploreState.favorites.decks.slice(0, 5).map((deckId, index) => ({
        id: deckId,
        name: `Deck Favori ${index + 1}`,
        cards_count: Math.floor(Math.random() * 200) + 20,
        category: Object.keys(exploreState.categories)[index % Object.keys(exploreState.categories).length]
    }));
    
    favoritesContainer.innerHTML = favoriteDecks.map(deck => {
        const category = exploreState.categories[deck.category] || exploreState.categories['other'];
        return `
            <div class="favorite-item" onclick="showPublicDeckDetails(${deck.id})">
                <div class="favorite-deck-item">
                    <div class="favorite-deck-icon">${category.icon}</div>
                    <div>
                        <div class="favorite-deck-name">${deck.name}</div>
                        <div class="favorite-deck-meta">${deck.cards_count} cartes</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updateFavoritesCount() {
    const countElement = document.getElementById('favoritesCount');
    if (countElement) {
        countElement.textContent = exploreState.favorites.decks.length;
    }
}

// Collections Management
async function loadCollections() {
    try {
        exploreState.collections.isLoading = true;
        const response = await exploreAPI.getCollections();
        exploreState.collections.list = response.results || [];
        renderCollections();
    } catch (error) {
        console.error('Error loading collections:', error);
        exploreState.collections.list = [];
        renderCollections();
    } finally {
        exploreState.collections.isLoading = false;
    }
}

function renderCollections() {
    const collectionsContainer = document.getElementById('myCollections');
    if (!collectionsContainer) return;
    
    if (exploreState.collections.list.length === 0) {
        collectionsContainer.innerHTML = `
            <div class="empty-collections">
                <i class="bi bi-heart"></i>
                <p>Aucune collection</p>
            </div>
        `;
        return;
    }
    
    collectionsContainer.innerHTML = exploreState.collections.list.map(collection => `
        <div class="collection-item" onclick="showManageCollectionModal(${collection.id})">
            <div class="collection-header">
                <div class="collection-name">${collection.name}</div>
                <div class="collection-count">${collection.deck_count || 0}</div>
            </div>
            <div class="collection-actions">
                <button class="collection-action-btn" onclick="event.stopPropagation(); editCollection(${collection.id})" title="Modifier">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="collection-action-btn" onclick="event.stopPropagation(); deleteCollectionConfirm(${collection.id})" title="Supprimer">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function showCreateCollectionModal() {
    const modal = new bootstrap.Modal(document.getElementById('createCollectionModal'));
    modal.show();
}

async function createCollection() {
    const name = document.getElementById('collectionName').value.trim();
    const description = document.getElementById('collectionDescription').value.trim();
    const visibility = document.querySelector('input[name="visibility"]:checked').value;
    
    if (!name) {
        window.notificationService?.error('Le nom de la collection est requis');
        return;
    }
    
    try {
        const newCollection = await exploreAPI.createCollection({
            name: name,
            description: description,
            visibility: visibility
        });
        
        exploreState.collections.list.push(newCollection);
        renderCollections();
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('createCollectionModal'));
        modal.hide();
        resetCreateCollectionForm();
        
        window.notificationService?.success(`Collection "${name}" créée avec succès 🎉`);
        
    } catch (error) {
        console.error('Error creating collection:', error);
        window.notificationService?.error('Erreur lors de la création de la collection');
    }
}

function resetCreateCollectionForm() {
    document.getElementById('collectionName').value = '';
    document.getElementById('collectionDescription').value = '';
    document.getElementById('privateCollection').checked = true;
}

async function showAddToCollectionModal(deckId) {
    exploreState.collections.deckToAdd = deckId;
    
    // Find deck info
    const deck = exploreState.publicDecks.find(d => d.id === deckId) || 
                 exploreState.selectedDeck && exploreState.selectedDeck.id === deckId ? exploreState.selectedDeck : null;
    
    if (!deck) {
        window.notificationService?.error('Deck introuvable');
        return;
    }
    
    // Update selected deck info in modal
    const selectedDeckInfo = document.getElementById('selectedDeckInfo');
    const category = exploreState.categories[deck.category] || exploreState.categories['other'];
    
    selectedDeckInfo.innerHTML = `
        <div class="selected-deck-preview">
            <div class="selected-deck-header">
                <div class="selected-deck-icon">${category.icon}</div>
                <div class="selected-deck-info">
                    <h6>${deck.name}</h6>
                    <div class="selected-deck-meta">
                        ${deck.cards_count || 0} cartes • Par @${deck.user.username}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Render collections list
    renderCollectionsInModal();
    
    const modal = new bootstrap.Modal(document.getElementById('addToCollectionModal'));
    modal.show();
}

function renderCollectionsInModal() {
    const collectionsList = document.getElementById('collectionsList');
    
    if (exploreState.collections.list.length === 0) {
        collectionsList.innerHTML = `
            <div class="text-center p-4 text-muted">
                <i class="bi bi-heart mb-2" style="font-size: 2rem;"></i>
                <p>Vous n'avez pas encore de collection.</p>
                <p class="small">Créez votre première collection ci-dessous !</p>
            </div>
        `;
        return;
    }
    
    collectionsList.innerHTML = exploreState.collections.list.map(collection => {
        const deckInCollection = collection.decks && collection.decks.some(d => d.id === exploreState.collections.deckToAdd);
        
        return `
            <div class="collection-option ${deckInCollection ? 'selected' : ''}" onclick="selectCollectionOption(${collection.id})">
                <div class="collection-option-header">
                    <div class="collection-option-name">${collection.name}</div>
                    <div class="collection-option-count">${collection.deck_count || 0} decks</div>
                </div>
                ${collection.description ? `<div class="collection-option-desc">${collection.description}</div>` : ''}
                ${deckInCollection ? '<div class="text-success small mt-1"><i class="bi bi-check-circle me-1"></i>Déjà dans cette collection</div>' : ''}
            </div>
        `;
    }).join('');
}

function selectCollectionOption(collectionId) {
    const options = document.querySelectorAll('.collection-option');
    options.forEach(option => option.classList.remove('selected'));
    
    const selectedOption = document.querySelector(`[onclick="selectCollectionOption(${collectionId})"]`);
    selectedOption.classList.add('selected');
    
    exploreState.collections.selected = collectionId;
    
    // Enable confirm button
    document.getElementById('addToCollectionConfirm').disabled = false;
}

async function addToCollection() {
    if (!exploreState.collections.selected || !exploreState.collections.deckToAdd) {
        window.notificationService?.error('Sélectionnez une collection');
        return;
    }
    
    try {
        await exploreAPI.addDeckToCollection(exploreState.collections.selected, exploreState.collections.deckToAdd);
        
        const collection = exploreState.collections.list.find(c => c.id === exploreState.collections.selected);
        window.notificationService?.success(`Deck ajouté à "${collection.name}" 📚`);
        
        // Update collections to refresh deck counts
        await loadCollections();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addToCollectionModal'));
        modal.hide();
        
        // Update deck cards display
        renderPublicDecks();
        
    } catch (error) {
        console.error('Error adding to collection:', error);
        window.notificationService?.error('Erreur lors de l\'ajout à la collection');
    }
}

function showManageCollectionModal(collectionId) {
    exploreState.collections.selected = collectionId;
    const collection = exploreState.collections.list.find(c => c.id === collectionId);
    
    if (!collection) return;
    
    // Fill form with collection data
    document.getElementById('editCollectionName').value = collection.name;
    document.getElementById('editCollectionDescription').value = collection.description || '';
    document.getElementById('editCollectionVisibility').value = collection.visibility || 'private';
    document.getElementById('manageCollectionTitle').innerHTML = `
        <i class="bi bi-gear me-2"></i>Gérer "${collection.name}"
    `;
    
    // Load collection decks
    loadCollectionDecks(collectionId);
    
    const modal = new bootstrap.Modal(document.getElementById('manageCollectionModal'));
    modal.show();
}

async function loadCollectionDecks(collectionId) {
    try {
        const response = await exploreAPI.getCollectionDecks(collectionId);
        const decks = response.results || [];
        
        const decksList = document.getElementById('collectionDecksList');
        const countBadge = document.getElementById('collectionDeckCount');
        
        countBadge.textContent = decks.length;
        
        if (decks.length === 0) {
            decksList.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="bi bi-folder2-open mb-2" style="font-size: 2rem;"></i>
                    <p>Cette collection est vide.</p>
                    <p class="small">Ajoutez des decks en explorant les decks publics !</p>
                </div>
            `;
            return;
        }
        
        decksList.innerHTML = decks.map(deck => {
            const category = exploreState.categories[deck.category] || exploreState.categories['other'];
            
            return `
                <div class="collection-deck-item">
                    <div class="collection-deck-icon">${category.icon}</div>
                    <div class="collection-deck-info">
                        <div class="collection-deck-name">${deck.name}</div>
                        <div class="collection-deck-meta">
                            ${deck.cards_count || 0} cartes • Par @${deck.user.username} • ${formatDate(deck.created_at)}
                        </div>
                    </div>
                    <div class="collection-deck-actions">
                        <button class="collection-deck-remove" onclick="removeDeckFromCollection(${collectionId}, ${deck.id})" title="Retirer de la collection">
                            <i class="bi bi-x-circle"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading collection decks:', error);
        document.getElementById('collectionDecksList').innerHTML = `
            <div class="text-center p-4 text-muted">
                <p>Erreur lors du chargement des decks.</p>
            </div>
        `;
    }
}

async function removeDeckFromCollection(collectionId, deckId) {
    try {
        await exploreAPI.removeDeckFromCollection(collectionId, deckId);
        window.notificationService?.success('Deck retiré de la collection');
        
        // Reload collection decks
        await loadCollectionDecks(collectionId);
        await loadCollections(); // Refresh counts
        
        // Update main deck display
        renderPublicDecks();
        
    } catch (error) {
        console.error('Error removing from collection:', error);
        window.notificationService?.error('Erreur lors de la suppression');
    }
}

async function saveCollectionChanges() {
    if (!exploreState.collections.selected) return;
    
    const name = document.getElementById('editCollectionName').value.trim();
    const description = document.getElementById('editCollectionDescription').value.trim();
    const visibility = document.getElementById('editCollectionVisibility').value;
    
    if (!name) {
        window.notificationService?.error('Le nom de la collection est requis');
        return;
    }
    
    try {
        await exploreAPI.updateCollection(exploreState.collections.selected, {
            name: name,
            description: description,
            visibility: visibility
        });
        
        // Update local state
        const collection = exploreState.collections.list.find(c => c.id === exploreState.collections.selected);
        if (collection) {
            collection.name = name;
            collection.description = description;
            collection.visibility = visibility;
        }
        
        renderCollections();
        window.notificationService?.success('Collection mise à jour');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('manageCollectionModal'));
        modal.hide();
        
    } catch (error) {
        console.error('Error updating collection:', error);
        window.notificationService?.error('Erreur lors de la mise à jour');
    }
}

async function deleteCollectionConfirm(collectionId) {
    const collection = exploreState.collections.list.find(c => c.id === collectionId);
    if (!collection) return;
    
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la collection "${collection.name}" ?\nCette action est irréversible.`)) {
        return;
    }
    
    try {
        await exploreAPI.deleteCollection(collectionId);
        
        // Remove from local state
        exploreState.collections.list = exploreState.collections.list.filter(c => c.id !== collectionId);
        renderCollections();
        
        window.notificationService?.success('Collection supprimée');
        
    } catch (error) {
        console.error('Error deleting collection:', error);
        window.notificationService?.error('Erreur lors de la suppression');
    }
}

// Event Listeners for Collections & Favorites
function setupFavoritesAndCollectionsEventListeners() {
    // Create collection button
    const createCollectionBtn = document.getElementById('createCollectionBtn');
    createCollectionBtn?.addEventListener('click', showCreateCollectionModal);
    
    // Create collection confirm
    const createCollectionConfirm = document.getElementById('createCollectionConfirm');
    createCollectionConfirm?.addEventListener('click', createCollection);
    
    // Add to collection confirm
    const addToCollectionConfirm = document.getElementById('addToCollectionConfirm');
    addToCollectionConfirm?.addEventListener('click', addToCollection);
    
    // Create new collection from modal
    const createNewFromModal = document.getElementById('createNewCollectionFromModal');
    createNewFromModal?.addEventListener('click', () => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('addToCollectionModal'));
        modal.hide();
        setTimeout(showCreateCollectionModal, 300);
    });
    
    // Save collection changes
    const saveCollectionChanges = document.getElementById('saveCollectionChanges');
    saveCollectionChanges?.addEventListener('click', saveCollectionChanges);
    
    // Delete collection button
    const deleteCollectionBtn = document.getElementById('deleteCollectionBtn');
    deleteCollectionBtn?.addEventListener('click', () => {
        if (exploreState.collections.selected) {
            deleteCollectionConfirm(exploreState.collections.selected);
        }
    });
}

// Make functions globally accessible
window.resetAdvancedSearch = resetAdvancedSearch;
window.applyAdvancedSearch = applyAdvancedSearch;
window.toggleFavorite = toggleFavorite;
window.showAddToCollectionModal = showAddToCollectionModal;
window.selectCollectionOption = selectCollectionOption;
window.showManageCollectionModal = showManageCollectionModal;
window.removeDeckFromCollection = removeDeckFromCollection;
// toggleSidebar function removed - now handled by inline onclick

// DOM Elements Helper
function getExploreElements() {
    return {
        // Sections
        exploreWelcome: document.getElementById('exploreWelcome'),
        exploreResults: document.getElementById('exploreResults'),
        publicDeckDetails: document.getElementById('publicDeckDetails'),
        
        // Sidebar
        exploreSidebar: document.getElementById('exploreSidebar'),
        popularDecks: document.getElementById('popularDecks'),
        
        // Filters
        exploreSearchInput: document.getElementById('exploreSearchInput'),
        authorFilter: document.getElementById('authorFilter'),
        categoryFilter: document.getElementById('categoryFilter'),
        languageFilter: document.getElementById('languageFilter'),
        levelFilter: document.getElementById('levelFilter'),
        ratingFilter: document.getElementById('ratingFilter'),
        sortByFilter: document.getElementById('sortBy'),
        minCards: document.getElementById('minCards'),
        maxCards: document.getElementById('maxCards'),
        
        // Buttons
        startExploring: document.getElementById('startExploring'),
        refreshPublicDecks: document.getElementById('refreshPublicDecks'),
        applyFilters: document.getElementById('applyFilters'),
        clearFilters: document.getElementById('clearFilters'),
        backToWelcome: document.getElementById('backToWelcome'),
        backToResults: document.getElementById('backToResults'),
        clearSearch: document.getElementById('clearSearch'),
        
        // Content
        publicDecksGrid: document.getElementById('publicDecksGrid'),
        exploreLoading: document.getElementById('exploreLoading'),
        noResults: document.getElementById('noResults'),
        explorePagination: document.getElementById('explorePagination'),
        
        // Stats
        totalPublicDecks: document.getElementById('totalDecksCount'),
        totalPublicCards: document.getElementById('totalCardsCount'),
        totalAuthors: document.getElementById('totalAuthorsCount'),
        resultsCount: document.getElementById('resultsCount'),
        
        // Public deck details
        publicDeckName: document.getElementById('publicDeckName'),
        publicDeckAuthor: document.getElementById('publicDeckAuthor'),
        publicDeckStats: document.getElementById('publicDeckStats'),
        publicDeckCardsPreview: document.getElementById('publicDeckCardsPreview'),
        publicDeckInfo: document.getElementById('publicDeckInfo'),
        importPublicDeck: document.getElementById('importPublicDeck'),
        
        // Import modal
        importModal: document.getElementById('importModal'),
        importDeckName: document.getElementById('importDeckName'),
        confirmImportDeck: document.getElementById('confirmImportDeck')
    };
}

// Event Listeners Setup
function setupExploreEventListeners() {
    const elements = getExploreElements();
    
    // Navigation
    elements.startExploring?.addEventListener('click', showExploreResults);
    elements.refreshPublicDecks?.addEventListener('click', () => loadPublicDecks());
    elements.backToWelcome?.addEventListener('click', showExploreWelcome);
    elements.backToResults?.addEventListener('click', showExploreResults);
    elements.clearSearch?.addEventListener('click', clearFilters);
    
    // Filters
    elements.exploreSearchInput?.addEventListener('input', debounce(() => {
        exploreState.filters.search = elements.exploreSearchInput.value;
        applyFilters();
    }, 300));
    
    elements.categoryFilter?.addEventListener('change', () => {
        exploreState.filters.category = elements.categoryFilter.value;
        applyFilters();
    });
    
    elements.languageFilter?.addEventListener('change', () => {
        exploreState.filters.language = elements.languageFilter.value;
        applyFilters();
    });
    
    elements.levelFilter?.addEventListener('change', () => {
        exploreState.filters.level = elements.levelFilter.value;
        applyFilters();
    });
    
    elements.ratingFilter?.addEventListener('change', () => {
        exploreState.filters.rating = elements.ratingFilter.value;
        applyFilters();
    });
    
    elements.sortByFilter?.addEventListener('change', () => {
        exploreState.filters.sortBy = elements.sortByFilter.value;
        applyFilters();
    });
    
    elements.authorFilter?.addEventListener('input', debounce(() => {
        exploreState.filters.author = elements.authorFilter.value;
        applyFilters();
    }, 300));
    
    elements.minCards?.addEventListener('input', debounce(() => {
        exploreState.filters.minCards = elements.minCards.value;
        applyFilters();
    }, 300));
    
    elements.maxCards?.addEventListener('input', debounce(() => {
        exploreState.filters.maxCards = elements.maxCards.value;
        applyFilters();
    }, 300));
    
    // Filter buttons
    elements.applyFilters?.addEventListener('click', applyFilters);
    elements.clearFilters?.addEventListener('click', clearFilters);
    
    // Import
    elements.importPublicDeck?.addEventListener('click', () => {
        if (exploreState.selectedDeck) {
            importPublicDeck(exploreState.selectedDeck.id);
        }
    });
    
    elements.confirmImportDeck?.addEventListener('click', confirmImportDeck);
    
    // View mode
    const gridViewBtn = document.getElementById('gridView');
    const listViewBtn = document.getElementById('listView');
    
    gridViewBtn?.addEventListener('change', () => {
        if (gridViewBtn.checked) setViewMode('grid');
    });
    
    listViewBtn?.addEventListener('change', () => {
        if (listViewBtn.checked) setViewMode('list');
    });
    
    // Load more reviews button
    const loadMoreReviewsBtn = document.getElementById('loadMoreReviews');
    loadMoreReviewsBtn?.addEventListener('click', loadMoreReviews);
}

// Initialize
function initializeExplore() {
    setupExploreEventListeners();
    setupFavoritesAndCollectionsEventListeners();
    initializeAdvancedSearch();
    showExploreResults(); // Changed from showExploreWelcome() to show search immediately
    loadPopularDecks();
    loadTrendingDecks();
    loadFavorites();
    loadCollections();
    
    // Load initial data
    loadPublicStats();
    
    // Initialize notification system
    setupNotificationEventListeners();
    loadNotifications();
    startNotificationPolling();
    
    // Initialize analytics system
    initializeAnalytics();
}

// ===== NOTIFICATION SYSTEM FUNCTIONS =====
async function toggleNotificationCenter() {
    const notificationCenter = document.getElementById('notificationCenter');
    const isVisible = exploreState.notifications.isVisible;
    
    if (isVisible) {
        notificationCenter.style.display = 'none';
        exploreState.notifications.isVisible = false;
        document.removeEventListener('click', closeNotificationOnClickOutside);
    } else {
        await loadNotifications();
        notificationCenter.style.display = 'block';
        exploreState.notifications.isVisible = true;
        document.addEventListener('click', closeNotificationOnClickOutside);
    }
}

function closeNotificationOnClickOutside(event) {
    const notificationCenter = document.getElementById('notificationCenter');
    const notificationBtn = document.getElementById('notificationBtn');
    
    if (!notificationCenter.contains(event.target) && !notificationBtn.contains(event.target)) {
        notificationCenter.style.display = 'none';
        exploreState.notifications.isVisible = false;
        document.removeEventListener('click', closeNotificationOnClickOutside);
    }
}

async function loadNotifications() {
    try {
        exploreState.notifications.isLoading = true;
        
        // Simulate API call with mock data for now
        const mockNotifications = generateMockNotifications();
        exploreState.notifications.list = mockNotifications;
        exploreState.notifications.unreadCount = mockNotifications.filter(n => !n.read).length;
        
        updateNotificationDisplay();
        updateNotificationBadge();
        updateNotificationFilters();
    } catch (error) {
        console.error('Error loading notifications:', error);
        showErrorToast('Erreur lors du chargement des notifications');
    } finally {
        exploreState.notifications.isLoading = false;
    }
}

function generateMockNotifications() {
    const now = new Date();
    return [
        {
            id: 1,
            type: 'new-decks',
            title: 'Nouveaux decks d\'anglais disponibles',
            text: '5 nouveaux decks de vocabulaire anglais ont été ajoutés par la communauté',
            time: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
            read: false,
            icon: 'bi-plus-circle',
            iconClass: 'new-deck'
        },
        {
            id: 2,
            type: 'favorites-updates',
            title: 'Mise à jour d\'un favori',
            text: 'Le deck "Vocabulaire Espagnol A2" a été mis à jour avec 20 nouvelles cartes',
            time: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(),
            read: false,
            icon: 'bi-heart-fill',
            iconClass: 'favorite-update'
        },
        {
            id: 3,
            type: 'collections-activity',
            title: 'Activité dans vos collections',
            text: 'Un nouveau deck a été ajouté à votre collection "Langues Européennes"',
            time: new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString(),
            read: true,
            icon: 'bi-collection',
            iconClass: 'collection-activity'
        },
        {
            id: 4,
            type: 'recommendations',
            title: 'Recommandation personnalisée',
            text: 'Basé sur votre activité, nous vous recommandons "Grammaire Française Avancée"',
            time: new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString(),
            read: true,
            icon: 'bi-star-fill',
            iconClass: 'recommendation'
        },
        {
            id: 5,
            type: 'system',
            title: 'Nouvelles fonctionnalités',
            text: 'Découvrez les nouvelles options de recherche vocale et de filtres avancés',
            time: new Date(now.getTime() - 48 * 60 * 60 * 1000).toISOString(),
            read: false,
            icon: 'bi-gear',
            iconClass: 'system'
        }
    ];
}

function updateNotificationDisplay() {
    const notificationList = document.getElementById('notificationList');
    const activeFilter = exploreState.notifications.activeFilter;
    let filteredNotifications = exploreState.notifications.list;

    if (activeFilter !== 'all') {
        filteredNotifications = filteredNotifications.filter(n => n.type === activeFilter);
    }

    if (filteredNotifications.length === 0) {
        notificationList.innerHTML = `
            <div class="notification-item placeholder">
                <div class="notification-icon">
                    <i class="bi bi-info-circle text-muted"></i>
                </div>
                <div class="notification-content">
                    <p class="notification-title">Aucune notification</p>
                    <p class="notification-text">Vous êtes à jour avec toutes les nouveautés!</p>
                    <small class="notification-time text-muted">Maintenant</small>
                </div>
            </div>
        `;
        return;
    }

    notificationList.innerHTML = filteredNotifications.map(notification => `
        <div class="notification-item ${!notification.read ? 'unread' : ''}" onclick="handleNotificationClick(${notification.id})">
            <div class="notification-icon ${notification.iconClass}">
                <i class="${notification.icon}"></i>
            </div>
            <div class="notification-content">
                <p class="notification-title">${notification.title}</p>
                <p class="notification-text">${notification.text}</p>
                <small class="notification-time">${formatNotificationTime(notification.time)}</small>
                <div class="notification-item-actions">
                    <button class="notification-action-btn primary" onclick="event.stopPropagation(); handleNotificationAction(${notification.id}, 'view')">
                        <i class="bi bi-eye me-1"></i>Voir
                    </button>
                    <button class="notification-action-btn secondary" onclick="event.stopPropagation(); dismissNotificationLocal(${notification.id})">
                        <i class="bi bi-x me-1"></i>Ignorer
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    const count = exploreState.notifications.unreadCount;
    
    if (count > 0 && exploreState.notifications.settings.badge) {
        badge.textContent = count > 99 ? '99+' : count.toString();
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

function updateNotificationFilters() {
    const notifications = exploreState.notifications.list;
    const counts = {
        all: notifications.length,
        'new-decks': notifications.filter(n => n.type === 'new-decks').length,
        'favorites-updates': notifications.filter(n => n.type === 'favorites-updates').length,
        'collections-activity': notifications.filter(n => n.type === 'collections-activity').length,
        system: notifications.filter(n => n.type === 'system').length
    };

    document.getElementById('allNotificationsCount').textContent = counts.all;
    document.getElementById('newDecksCount').textContent = counts['new-decks'];
    document.getElementById('favoritesUpdatesCount').textContent = counts['favorites-updates'];
    document.getElementById('collectionsActivityCount').textContent = counts['collections-activity'];
    document.getElementById('systemNotificationsCount').textContent = counts.system;
}

function formatNotificationTime(timeString) {
    const time = new Date(timeString);
    const now = new Date();
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `${diffMins}min`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}j`;
    
    return time.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
}

function filterNotifications(filterType) {
    exploreState.notifications.activeFilter = filterType;
    
    // Update filter button states
    document.querySelectorAll('.notification-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${filterType}"]`).classList.add('active');
    
    updateNotificationDisplay();
}

async function handleNotificationClick(notificationId) {
    const notification = exploreState.notifications.list.find(n => n.id === notificationId);
    if (!notification) return;

    // Mark as read if unread
    if (!notification.read) {
        await markNotificationReadLocal(notificationId);
    }

    // Handle different notification types
    switch (notification.type) {
        case 'new-decks':
            await loadPublicDecks(1);
            showSuccessToast('Affichage des nouveaux decks');
            break;
        case 'favorites-updates':
            const favoritesSection = document.querySelector('.sidebar-favorites');
            if (favoritesSection) {
                favoritesSection.scrollIntoView({ behavior: 'smooth' });
            }
            break;
        case 'collections-activity':
            const collectionsSection = document.querySelector('.sidebar-collections');
            if (collectionsSection) {
                collectionsSection.scrollIntoView({ behavior: 'smooth' });
            }
            break;
        case 'recommendations':
            // Could open a recommendations modal or filter
            applyFilters();
            break;
    }
    
    // Close notification center
    toggleNotificationCenter();
}

function handleNotificationAction(notificationId, action) {
    const notification = exploreState.notifications.list.find(n => n.id === notificationId);
    if (!notification) return;

    switch (action) {
        case 'view':
            handleNotificationClick(notificationId);
            break;
        case 'dismiss':
            dismissNotificationLocal(notificationId);
            break;
    }
}

async function markNotificationReadLocal(notificationId) {
    const notification = exploreState.notifications.list.find(n => n.id === notificationId);
    if (notification && !notification.read) {
        notification.read = true;
        exploreState.notifications.unreadCount = Math.max(0, exploreState.notifications.unreadCount - 1);
        
        updateNotificationBadge();
        updateNotificationDisplay();
        
        try {
            await exploreAPI.markNotificationRead(notificationId);
        } catch (error) {
            console.error('Error marking notification as read:', error);
            // Revert on error
            notification.read = false;
            exploreState.notifications.unreadCount += 1;
            updateNotificationBadge();
        }
    }
}

async function markAllNotificationsRead() {
    const unreadNotifications = exploreState.notifications.list.filter(n => !n.read);
    
    // Optimistically update UI
    unreadNotifications.forEach(notification => {
        notification.read = true;
    });
    exploreState.notifications.unreadCount = 0;
    
    updateNotificationBadge();
    updateNotificationDisplay();
    
    try {
        await exploreAPI.markAllNotificationsRead();
        showSuccessToast('Toutes les notifications ont été marquées comme lues');
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
        // Revert on error
        unreadNotifications.forEach(notification => {
            notification.read = false;
        });
        exploreState.notifications.unreadCount = unreadNotifications.length;
        updateNotificationBadge();
        showErrorToast('Erreur lors du marquage des notifications');
    }
}

function dismissNotificationLocal(notificationId) {
    const notificationIndex = exploreState.notifications.list.findIndex(n => n.id === notificationId);
    if (notificationIndex > -1) {
        const notification = exploreState.notifications.list[notificationIndex];
        
        // Add animation class
        const notificationElement = document.querySelector(`[onclick*="handleNotificationClick(${notificationId})"]`);
        if (notificationElement) {
            notificationElement.classList.add('animate-remove');
            
            setTimeout(() => {
                exploreState.notifications.list.splice(notificationIndex, 1);
                if (!notification.read) {
                    exploreState.notifications.unreadCount = Math.max(0, exploreState.notifications.unreadCount - 1);
                }
                updateNotificationDisplay();
                updateNotificationBadge();
                updateNotificationFilters();
            }, 300);
        }
        
        // API call to dismiss
        exploreAPI.dismissNotification(notificationId).catch(error => {
            console.error('Error dismissing notification:', error);
        });
    }
}

function showNotificationSettings() {
    const modal = new bootstrap.Modal(document.getElementById('notificationSettingsModal'));
    loadNotificationSettingsToModal();
    modal.show();
}

function loadNotificationSettingsToModal() {
    const settings = exploreState.notifications.settings;
    
    document.getElementById('enableNotifications').checked = settings.enabled;
    document.getElementById('enableSoundNotifications').checked = settings.sounds;
    document.getElementById('enableBadgeNotifications').checked = settings.badge;
    document.getElementById('notifyNewDecks').checked = settings.newDecks;
    document.getElementById('notifyFavoritesUpdates').checked = settings.favoritesUpdates;
    document.getElementById('notifyCollectionsActivity').checked = settings.collectionsActivity;
    document.getElementById('notifyRecommendations').checked = settings.recommendations;
    document.getElementById('notifySystem').checked = settings.system;
    document.getElementById('notificationFrequency').value = settings.frequency;
}

async function saveNotificationSettings() {
    const settings = {
        enabled: document.getElementById('enableNotifications').checked,
        sounds: document.getElementById('enableSoundNotifications').checked,
        badge: document.getElementById('enableBadgeNotifications').checked,
        newDecks: document.getElementById('notifyNewDecks').checked,
        favoritesUpdates: document.getElementById('notifyFavoritesUpdates').checked,
        collectionsActivity: document.getElementById('notifyCollectionsActivity').checked,
        recommendations: document.getElementById('notifyRecommendations').checked,
        system: document.getElementById('notifySystem').checked,
        frequency: document.getElementById('notificationFrequency').value
    };
    
    try {
        exploreState.notifications.settings = settings;
        localStorage.setItem('linguify_notification_settings', JSON.stringify(settings));
        
        await exploreAPI.updateNotificationSettings(settings);
        
        // Update badge visibility based on new settings
        updateNotificationBadge();
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('notificationSettingsModal'));
        modal.hide();
        
        showSuccessToast('Paramètres de notifications sauvegardés');
    } catch (error) {
        console.error('Error saving notification settings:', error);
        showErrorToast('Erreur lors de la sauvegarde des paramètres');
    }
}

function showAllNotifications() {
    const modal = new bootstrap.Modal(document.getElementById('allNotificationsModal'));
    loadAllNotificationsToModal();
    modal.show();
    toggleNotificationCenter(); // Close the dropdown
}

function loadAllNotificationsToModal() {
    const notificationFullList = document.getElementById('notificationFullList');
    const notifications = exploreState.notifications.list;
    
    if (notifications.length === 0) {
        notificationFullList.innerHTML = `
            <div class="text-center p-4">
                <i class="bi bi-bell text-muted" style="font-size: 3rem;"></i>
                <h5 class="mt-3 text-muted">Aucune notification</h5>
                <p class="text-muted">Toutes vos notifications apparaîtront ici.</p>
            </div>
        `;
        return;
    }

    notificationFullList.innerHTML = notifications.map(notification => `
        <div class="notification-item ${!notification.read ? 'unread' : ''}" onclick="handleNotificationClick(${notification.id})">
            <div class="notification-icon ${notification.iconClass}">
                <i class="${notification.icon}"></i>
            </div>
            <div class="notification-content">
                <p class="notification-title">${notification.title}</p>
                <p class="notification-text">${notification.text}</p>
                <small class="notification-time">${formatNotificationTime(notification.time)}</small>
                <div class="notification-item-actions">
                    <button class="notification-action-btn primary" onclick="event.stopPropagation(); handleNotificationAction(${notification.id}, 'view')">
                        <i class="bi bi-eye me-1"></i>Voir
                    </button>
                    <button class="notification-action-btn secondary" onclick="event.stopPropagation(); dismissNotificationLocal(${notification.id})">
                        <i class="bi bi-x me-1"></i>Supprimer
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function setupNotificationEventListeners() {
    // Notification filter buttons
    document.querySelectorAll('.notification-filter').forEach(btn => {
        btn.addEventListener('click', () => {
            filterNotifications(btn.dataset.filter);
        });
    });
    
    // Close notification center when clicking outside
    document.addEventListener('click', (event) => {
        const notificationCenter = document.getElementById('notificationCenter');
        const notificationBtn = document.getElementById('notificationBtn');
        
        if (exploreState.notifications.isVisible && 
            !notificationCenter.contains(event.target) && 
            !notificationBtn.contains(event.target)) {
            toggleNotificationCenter();
        }
    });
}

// Periodic notification check
function startNotificationPolling() {
    if (!exploreState.notifications.settings.enabled) return;
    
    const frequency = exploreState.notifications.settings.frequency;
    let intervalMs;
    
    switch (frequency) {
        case 'realtime':
            intervalMs = 30000; // 30 seconds
            break;
        case 'hourly':
            intervalMs = 3600000; // 1 hour
            break;
        case 'daily':
            intervalMs = 86400000; // 24 hours
            break;
        case 'weekly':
            intervalMs = 604800000; // 7 days
            break;
        default:
            intervalMs = 86400000;
    }
    
    setInterval(async () => {
        if (document.visibilityState === 'visible') {
            await checkForNewNotifications();
        }
    }, intervalMs);
}

async function checkForNewNotifications() {
    try {
        // In a real implementation, this would check the server for new notifications
        // For now, we'll simulate occasional new notifications
        if (Math.random() < 0.1) { // 10% chance
            addMockNotification();
        }
    } catch (error) {
        console.error('Error checking for new notifications:', error);
    }
}

function addMockNotification() {
    const mockNotifications = [
        {
            type: 'new-decks',
            title: 'Nouveau deck ajouté!',
            text: 'Un nouveau deck de japonais vient d\'être publié par un utilisateur',
            icon: 'bi-plus-circle',
            iconClass: 'new-deck'
        },
        {
            type: 'recommendations',
            title: 'Nouvelle recommandation',
            text: 'Nous avons trouvé un deck qui pourrait vous intéresser',
            icon: 'bi-star-fill',
            iconClass: 'recommendation'
        }
    ];
    
    const randomNotification = mockNotifications[Math.floor(Math.random() * mockNotifications.length)];
    const notification = {
        id: Date.now(),
        ...randomNotification,
        time: new Date().toISOString(),
        read: false
    };
    
    exploreState.notifications.list.unshift(notification);
    exploreState.notifications.unreadCount += 1;
    
    updateNotificationBadge();
    
    // Show toast notification if enabled
    if (exploreState.notifications.settings.sounds) {
        // In a real implementation, play notification sound
        console.log('🔔 Notification sound would play here');
    }
    
    showInfoToast(`Nouvelle notification: ${notification.title}`, 3000);
}

// ===== ANALYTICS SYSTEM FUNCTIONS =====
function initializeAnalytics() {
    // Record page load time
    exploreState.analytics.performanceMetrics.pageLoadTime = performance.now();
    
    // Track session start
    trackEvent('session_start', {
        page: 'explore',
        userAgent: navigator.userAgent,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        timestamp: exploreState.analytics.sessionStart
    });
    
    // Set up global analytics event listeners
    setupAnalyticsEventListeners();
    
    // Start periodic analytics collection
    startAnalyticsCollection();
    
    // Track page entry point
    trackEntryPoint();
    
    // Setup performance observers
    setupPerformanceObservers();
}

function trackEvent(eventType, eventData = {}) {
    const event = {
        type: eventType,
        data: eventData,
        timestamp: new Date().toISOString(),
        sessionId: exploreState.analytics.sessionStart,
        url: window.location.href
    };
    
    // Store locally
    exploreState.analytics.interactions.push(event);
    
    // Update metrics
    updateAnalyticsMetrics(eventType, eventData);
    
    // Send to server (with throttling)
    sendAnalyticsEventAsync(event);
    
    console.log('📊 Analytics Event:', eventType, eventData);
}

function updateAnalyticsMetrics(eventType, eventData) {
    const metrics = exploreState.analytics.metrics;
    
    switch (eventType) {
        case 'search_query':
            metrics.searchQueries++;
            updateSearchHeatmap(eventData.query);
            break;
        case 'deck_viewed':
            metrics.decksViewed++;
            updateCategoryHeatmap(eventData.category);
            updateAuthorHeatmap(eventData.author);
            break;
        case 'deck_imported':
            metrics.decksImported++;
            break;
        case 'favorite_added':
            metrics.favoritesAdded++;
            break;
        case 'collection_created':
            metrics.collectionsCreated++;
            break;
        case 'filter_applied':
            metrics.filtersApplied++;
            if (eventData.language) updateLanguageHeatmap(eventData.language);
            if (eventData.category) updateCategoryHeatmap(eventData.category);
            break;
        case 'popular_deck_viewed':
            metrics.popularDecksViewed++;
            break;
        case 'trending_deck_viewed':
            metrics.trendingDecksViewed++;
            break;
        case 'notification_clicked':
            metrics.notificationClicks++;
            break;
    }
    
    // Update time spent
    metrics.timeSpent = Math.floor((new Date() - new Date(exploreState.analytics.sessionStart)) / 1000);
}

function updateSearchHeatmap(query) {
    if (!query || query.length < 2) return;
    
    const heatmap = exploreState.analytics.heatmap.searchTerms;
    const normalizedQuery = query.toLowerCase().trim();
    
    heatmap[normalizedQuery] = (heatmap[normalizedQuery] || 0) + 1;
    localStorage.setItem('linguify_search_heatmap', JSON.stringify(heatmap));
}

function updateCategoryHeatmap(category) {
    if (!category) return;
    
    const heatmap = exploreState.analytics.heatmap.categories;
    heatmap[category] = (heatmap[category] || 0) + 1;
    localStorage.setItem('linguify_category_heatmap', JSON.stringify(heatmap));
}

function updateAuthorHeatmap(author) {
    if (!author) return;
    
    const heatmap = exploreState.analytics.heatmap.authors;
    heatmap[author] = (heatmap[author] || 0) + 1;
    localStorage.setItem('linguify_author_heatmap', JSON.stringify(heatmap));
}

function updateLanguageHeatmap(language) {
    if (!language) return;
    
    const heatmap = exploreState.analytics.heatmap.languages;
    heatmap[language] = (heatmap[language] || 0) + 1;
    localStorage.setItem('linguify_language_heatmap', JSON.stringify(heatmap));
}

function setupAnalyticsEventListeners() {
    // Track clicks
    document.addEventListener('click', (event) => {
        const element = event.target;
        const tag = element.tagName.toLowerCase();
        const className = element.className;
        const id = element.id;
        
        // Record click heatmap
        const rect = element.getBoundingClientRect();
        exploreState.analytics.userBehavior.clickHeatmap.push({
            x: event.clientX,
            y: event.clientY,
            element: tag,
            className: className,
            id: id,
            timestamp: new Date().toISOString()
        });
        
        // Track specific interactions
        if (element.closest('.public-deck-card')) {
            const deckId = element.closest('.public-deck-card').dataset.deckId;
            if (deckId) {
                trackEvent('deck_card_clicked', { 
                    deckId: deckId,
                    cardPosition: getCardPosition(element.closest('.public-deck-card'))
                });
            }
        }
        
        if (element.closest('.deck-action-btn')) {
            trackEvent('deck_action_clicked', { 
                action: element.classList.contains('favorite-btn') ? 'favorite' : 'collection',
                deckId: element.closest('.public-deck-card')?.dataset.deckId
            });
        }
        
        if (element.closest('.notification-item')) {
            trackEvent('notification_clicked', { 
                notificationId: element.closest('.notification-item').dataset.notificationId
            });
        }
    });
    
    // Track scroll depth
    let maxScrollDepth = 0;
    document.addEventListener('scroll', throttle(() => {
        const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
        if (scrollPercent > maxScrollDepth) {
            maxScrollDepth = scrollPercent;
            exploreState.analytics.userBehavior.scrollDepth = maxScrollDepth;
            
            // Track scroll milestones
            if (scrollPercent >= 25 && maxScrollDepth < 25) trackEvent('scroll_25');
            if (scrollPercent >= 50 && maxScrollDepth < 50) trackEvent('scroll_50');
            if (scrollPercent >= 75 && maxScrollDepth < 75) trackEvent('scroll_75');
            if (scrollPercent >= 90 && maxScrollDepth < 90) trackEvent('scroll_90');
        }
    }, 500));
    
    // Track focus/blur for dwell time
    const elements = document.querySelectorAll('.public-deck-card, .sidebar-section, .notification-item');
    elements.forEach(element => {
        let focusStartTime;
        
        element.addEventListener('mouseenter', () => {
            focusStartTime = Date.now();
        });
        
        element.addEventListener('mouseleave', () => {
            if (focusStartTime) {
                const dwellTime = Date.now() - focusStartTime;
                const elementId = element.id || element.className;
                
                if (!exploreState.analytics.userBehavior.dwellTime[elementId]) {
                    exploreState.analytics.userBehavior.dwellTime[elementId] = [];
                }
                exploreState.analytics.userBehavior.dwellTime[elementId].push(dwellTime);
                
                // Track significant dwell times (>3 seconds)
                if (dwellTime > 3000) {
                    trackEvent('significant_dwell', { 
                        element: elementId,
                        dwellTime: dwellTime
                    });
                }
            }
        });
    });
    
    // Track window focus/blur
    let tabFocusTime = Date.now();
    window.addEventListener('focus', () => {
        tabFocusTime = Date.now();
        trackEvent('tab_focused');
    });
    
    window.addEventListener('blur', () => {
        const timeSpent = Date.now() - tabFocusTime;
        trackEvent('tab_blurred', { timeSpent });
    });
    
    // Track page visibility
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            trackEvent('page_hidden');
        } else {
            trackEvent('page_visible');
        }
    });
}

function getCardPosition(cardElement) {
    const cards = document.querySelectorAll('.public-deck-card');
    return Array.from(cards).indexOf(cardElement);
}

function throttle(func, delay) {
    let timeoutId;
    let lastExecTime = 0;
    return function (...args) {
        const currentTime = Date.now();
        
        if (currentTime - lastExecTime > delay) {
            func.apply(this, args);
            lastExecTime = currentTime;
        } else {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
                lastExecTime = Date.now();
            }, delay - (currentTime - lastExecTime));
        }
    };
}

function setupPerformanceObservers() {
    // Observe API response times
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const startTime = performance.now();
        const url = args[0];
        
        return originalFetch.apply(this, args)
            .then(response => {
                const endTime = performance.now();
                const responseTime = endTime - startTime;
                
                exploreState.analytics.performanceMetrics.apiResponseTimes.push({
                    url: url,
                    responseTime: responseTime,
                    status: response.status,
                    timestamp: new Date().toISOString()
                });
                
                // Track slow responses (>2 seconds)
                if (responseTime > 2000) {
                    trackEvent('slow_api_response', { 
                        url: url,
                        responseTime: responseTime
                    });
                }
                
                return response;
            })
            .catch(error => {
                exploreState.analytics.performanceMetrics.errorCount++;
                trackEvent('api_error', { 
                    url: url,
                    error: error.message
                });
                throw error;
            });
    };
    
    // Observe resource loading performance
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (entry.entryType === 'navigation') {
                    trackEvent('navigation_timing', {
                        domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                        loadComplete: entry.loadEventEnd - entry.loadEventStart,
                        totalTime: entry.loadEventEnd - entry.fetchStart
                    });
                }
                
                if (entry.entryType === 'resource' && entry.duration > 1000) {
                    trackEvent('slow_resource', {
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize
                    });
                }
            });
        });
        
        observer.observe({ entryTypes: ['navigation', 'resource'] });
    }
}

function trackEntryPoint() {
    const referrer = document.referrer;
    const urlParams = new URLSearchParams(window.location.search);
    const source = urlParams.get('source') || 'direct';
    
    exploreState.analytics.userBehavior.entryPoints.push({
        referrer: referrer,
        source: source,
        timestamp: new Date().toISOString()
    });
    
    trackEvent('page_entry', { 
        referrer: referrer,
        source: source
    });
}

function startAnalyticsCollection() {
    // Collect and send analytics every 30 seconds
    setInterval(() => {
        collectAndSendAnalytics();
    }, 30000);
    
    // Send analytics on page unload
    window.addEventListener('beforeunload', () => {
        collectAndSendAnalytics(true);
    });
}

function collectAndSendAnalytics(isUnload = false) {
    const sessionData = {
        sessionId: exploreState.analytics.sessionStart,
        metrics: exploreState.analytics.metrics,
        heatmap: exploreState.analytics.heatmap,
        performanceMetrics: exploreState.analytics.performanceMetrics,
        userBehavior: exploreState.analytics.userBehavior,
        interactions: exploreState.analytics.interactions.slice(-10), // Last 10 interactions
        sessionDuration: Math.floor((new Date() - new Date(exploreState.analytics.sessionStart)) / 1000),
        isSessionEnd: isUnload
    };
    
    if (isUnload) {
        // Use sendBeacon for reliable delivery on page unload
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/v1/analytics/sessions/', JSON.stringify(sessionData));
        }
    } else {
        exploreAPI.submitAnalyticsSession(sessionData).catch(error => {
            console.error('Analytics submission failed:', error);
        });
    }
}

async function sendAnalyticsEventAsync(event) {
    // Throttle individual event sending to avoid spam
    if (!sendAnalyticsEventAsync.queue) {
        sendAnalyticsEventAsync.queue = [];
        sendAnalyticsEventAsync.sending = false;
    }
    
    sendAnalyticsEventAsync.queue.push(event);
    
    if (!sendAnalyticsEventAsync.sending && sendAnalyticsEventAsync.queue.length >= 5) {
        sendAnalyticsEventAsync.sending = true;
        
        const eventsToSend = sendAnalyticsEventAsync.queue.splice(0, 10); // Send max 10 at once
        
        try {
            await Promise.all(
                eventsToSend.map(evt => exploreAPI.trackEvent(evt.type, evt.data))
            );
        } catch (error) {
            console.error('Failed to send analytics events:', error);
            // Re-add failed events to queue
            sendAnalyticsEventAsync.queue.unshift(...eventsToSend);
        } finally {
            sendAnalyticsEventAsync.sending = false;
        }
    }
}

function generateAnalyticsReport() {
    const metrics = exploreState.analytics.metrics;
    const sessionDuration = Math.floor((new Date() - new Date(exploreState.analytics.sessionStart)) / 1000);
    
    return {
        session: {
            duration: sessionDuration,
            startTime: exploreState.analytics.sessionStart,
            interactions: exploreState.analytics.interactions.length
        },
        engagement: {
            searchQueries: metrics.searchQueries,
            decksViewed: metrics.decksViewed,
            decksImported: metrics.decksImported,
            favoritesAdded: metrics.favoritesAdded,
            collectionsCreated: metrics.collectionsCreated,
            scrollDepth: exploreState.analytics.userBehavior.scrollDepth
        },
        performance: {
            pageLoadTime: exploreState.analytics.performanceMetrics.pageLoadTime,
            averageApiResponseTime: calculateAverageResponseTime(),
            errorCount: exploreState.analytics.performanceMetrics.errorCount
        },
        heatmaps: {
            topSearchTerms: getTopItems(exploreState.analytics.heatmap.searchTerms, 5),
            topCategories: getTopItems(exploreState.analytics.heatmap.categories, 5),
            topLanguages: getTopItems(exploreState.analytics.heatmap.languages, 5)
        }
    };
}

function calculateAverageResponseTime() {
    const times = exploreState.analytics.performanceMetrics.apiResponseTimes;
    if (times.length === 0) return 0;
    
    const sum = times.reduce((acc, time) => acc + time.responseTime, 0);
    return Math.round(sum / times.length);
}

function getTopItems(heatmap, limit = 5) {
    return Object.entries(heatmap)
        .sort(([,a], [,b]) => b - a)
        .slice(0, limit)
        .reduce((obj, [key, value]) => {
            obj[key] = value;
            return obj;
        }, {});
}

// Enhanced tracking functions for existing functionality
function trackSearch(query) {
    trackEvent('search_query', { 
        query: query,
        queryLength: query.length,
        hasFilters: Object.keys(exploreState.filters).some(key => key !== 'search' && exploreState.filters[key])
    });
}

function trackDeckView(deck) {
    trackEvent('deck_viewed', {
        deckId: deck.id,
        title: deck.title,
        author: deck.author,
        category: deck.category,
        cardCount: deck.card_count,
        rating: deck.rating,
        viewSource: getViewSource()
    });
}

function trackDeckImport(deck) {
    trackEvent('deck_imported', {
        deckId: deck.id,
        title: deck.title,
        author: deck.author,
        category: deck.category,
        cardCount: deck.card_count,
        importTime: new Date().toISOString()
    });
}

function trackFilter(filterType, filterValue) {
    trackEvent('filter_applied', {
        filterType: filterType,
        filterValue: filterValue,
        activeFilters: Object.keys(exploreState.filters).filter(key => exploreState.filters[key])
    });
}

function getViewSource() {
    if (exploreState.search.isActive) return 'search';
    if (document.querySelector('.popular-decks:visible')) return 'popular';
    if (document.querySelector('.trending-decks:visible')) return 'trending';
    return 'browse';
}

// Global exports
window.exploreMain = {
    initializeExplore,
    showExploreWelcome,
    showExploreResults,
    showPublicDeckDetails,
    importPublicDeck,
    confirmImportDeck,
    loadPublicDecks,
    loadTrendingDecks,
    setViewMode,
    setUserRating,
    highlightStars,
    markReviewHelpful,
    loadMoreReviews,
    applyFilters,
    clearFilters,
    exploreState,
    exploreAPI
};

// Make functions globally accessible for onclick handlers
window.setUserRating = setUserRating;
window.markReviewHelpful = markReviewHelpful;
window.loadMoreReviews = loadMoreReviews;
window.showPublicDeckDetails = showPublicDeckDetails;
window.toggleNotificationCenter = toggleNotificationCenter;
window.markAllNotificationsRead = markAllNotificationsRead;
window.showNotificationSettings = showNotificationSettings;
window.saveNotificationSettings = saveNotificationSettings;
window.showAllNotifications = showAllNotifications;
window.handleNotificationClick = handleNotificationClick;
window.handleNotificationAction = handleNotificationAction;
window.dismissNotificationLocal = dismissNotificationLocal;
window.filterNotifications = filterNotifications;

// ===== PERFORMANCE OPTIMIZATION FUNCTIONS =====
function optimizePerformance() {
    // Enable passive event listeners for better scroll performance
    ['scroll', 'touchmove', 'wheel'].forEach(event => {
        document.addEventListener(event, () => {}, { passive: true });
    });
    
    // Preload critical resources
    preloadCriticalResources();
    
    // Setup intersection observer for lazy loading
    setupLazyLoading();
    
    // Debounce resize events
    window.addEventListener('resize', debounce(() => {
        trackEvent('viewport_resize', {
            width: window.innerWidth,
            height: window.innerHeight
        });
    }, 250));
    
    // Optimize font loading
    if ('fonts' in document) {
        document.fonts.ready.then(() => {
            trackEvent('fonts_loaded', { fontCount: document.fonts.size });
        });
    }
}

function preloadCriticalResources() {
    // Preload common API endpoints
    const criticalEndpoints = [
        '/api/v1/revision/public/stats/',
        '/api/v1/revision/public/trending/',
        '/api/v1/revision/public/popular/'
    ];
    
    criticalEndpoints.forEach(endpoint => {
        const link = document.createElement('link');
        link.rel = 'dns-prefetch';
        link.href = endpoint;
        document.head.appendChild(link);
    });
    
    // Preload critical images
    const criticalImages = [
        '{% static "revision/images/explore-hero.webp" %}',
        '{% static "revision/images/community-icon.svg" %}'
    ];
    
    criticalImages.forEach(src => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = src;
        document.head.appendChild(link);
    });
}

function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const lazyImageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    lazyImageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            lazyImageObserver.observe(img);
        });
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimize heavy functions with memoization
const memoize = (fn) => {
    const cache = new Map();
    return (...args) => {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = fn(...args);
        cache.set(key, result);
        return result;
    };
};

// Memoize expensive functions
const memoizedFormatTime = memoize(formatNotificationTime);
const memoizedGetTopItems = memoize(getTopItems);

// Critical path optimization - prioritize above-the-fold content
function prioritizeCriticalPath() {
    // Load essential components first
    return Promise.all([
        loadPublicStats(),
        loadNotifications()
    ]).then(() => {
        // Then load secondary components
        return Promise.all([
            loadPopularDecks(),
            loadTrendingDecks(),
            loadFavorites(),
            loadCollections()
        ]);
    });
}

// Service Worker registration for caching
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/revision/explorer/sw.js')
            .then(registration => {
                trackEvent('service_worker_registered', {
                    scope: registration.scope
                });
            })
            .catch(error => {
                console.error('SW registration failed:', error);
            });
    }
}

// Optimized initialization with performance monitoring
async function initializeExploreOptimized() {
    const initStartTime = performance.now();
    
    try {
        // Performance optimizations
        optimizePerformance();
        
        // Register service worker for caching
        registerServiceWorker();
        
        // Setup event listeners
        setupExploreEventListeners();
        setupFavoritesAndCollectionsEventListeners();
        
        // Initialize advanced search
        initializeAdvancedSearch();
        
        // Initialize analytics first for tracking
        initializeAnalytics();
        
        // Show welcome screen immediately
        showExploreResults(); // Changed from showExploreWelcome() to show search immediately
        
        // Sidebar is shown by default with 'show' class in template
        
        // Load critical path components
        await prioritizeCriticalPath();
        
        // Initialize notification system
        setupNotificationEventListeners();
        startNotificationPolling();
        
        const initEndTime = performance.now();
        trackEvent('initialization_complete', {
            initTime: initEndTime - initStartTime,
            memoryUsage: performance.memory ? performance.memory.usedJSHeapSize : null
        });
        
    } catch (error) {
        console.error('Initialization failed:', error);
        trackEvent('initialization_error', { error: error.message });
    }
}

// Refresh function removed - now handled by HTMX

// Auto-initialize when DOM is ready with optimizations
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeExploreOptimized);
} else {
    initializeExploreOptimized();
}