// Revision Explore Interface Manager
// État global pour l'exploration
let exploreState = {
    publicDecks: [],
    popularDecks: [],
    currentPage: 1,
    totalPages: 1,
    totalDecks: 0,
    isLoading: false,
    selectedDeck: null,
    filters: {
        search: '',
        author: '',
        sortBy: 'created_at',
        minCards: '',
        maxCards: ''
    },
    stats: {
        totalDecks: 0,
        totalCards: 0,
        totalAuthors: 0
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
        
        const [deck, cards] = await Promise.all([
            exploreAPI.getPublicDeck(deckId),
            exploreAPI.getPublicDeckCards(deckId)
        ]);
        
        exploreState.selectedDeck = { ...deck, cards };
        
        hideLoading();
        renderPublicDeckDetails();
        
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
    
    container.innerHTML = exploreState.publicDecks.map(deck => `
        <div class="col-md-6 col-lg-4">
            <div class="public-deck-card card h-100" onclick="showPublicDeckDetails(${deck.id})">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1 fw-bold">${deck.name}</h6>
                            <small class="text-muted">
                                Par <span class="deck-author">@${deck.user.username}</span>
                            </small>
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
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="bi bi-calendar3 me-1"></i>
                            ${formatDate(deck.created_at)}
                        </small>
                        <button class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); importPublicDeck(${deck.id})">
                            <i class="bi bi-download me-1"></i>
                            Importer
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
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
    
    container.innerHTML = exploreState.popularDecks.map(deck => `
        <div class="popular-deck-item" onclick="showPublicDeckDetails(${deck.id})">
            <div class="fw-bold small">${deck.name}</div>
            <div class="text-muted tiny">
                ${deck.cards_count || 0} cartes • @${deck.user.username}
            </div>
        </div>
    `).join('');
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
        sortBy: 'created_at',
        minCards: '',
        maxCards: ''
    };
    
    elements.exploreSearchInput.value = '';
    elements.authorFilter.value = '';
    elements.sortByFilter.value = 'created_at';
    elements.minCards.value = '';
    elements.maxCards.value = '';
    
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
        sortByFilter: document.getElementById('sortByFilter'),
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
        totalPublicDecks: document.getElementById('totalPublicDecks'),
        totalPublicCards: document.getElementById('totalPublicCards'),
        totalAuthors: document.getElementById('totalAuthors'),
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
    
    // Note: Le filtre par langue sera ajouté dans une version future
    
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
}

// Initialize
function initializeExplore() {
    setupExploreEventListeners();
    showExploreWelcome();
    loadPopularDecks();
    
    // Load initial data
    loadPublicStats();
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
    applyFilters,
    clearFilters,
    exploreState,
    exploreAPI
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeExplore);