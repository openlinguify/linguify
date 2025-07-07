// Revision Main Interface Manager
// État global de l'application
let appState = {
    decks: [],
    selectedDeck: null,
    isLoading: false,
    currentPage: 1,
    hasMore: true,
    stats: {
        totalDecks: 0,
        totalCards: 0,
        totalLearned: 0,
        completionRate: 0
    },
    filters: {
        search: '',
        status: '',
        sort: 'updated_desc'
    }
};

// API Service optimisé
const revisionAPI = {
    async getDecks(page = 1, filters = {}) {
        const params = new URLSearchParams({
            page: page,
            ...filters
        });
        
        return await window.apiService.request(`/api/v1/revision/decks/?${params}`);
    },
    
    async getDeck(id) {
        return await window.apiService.request(`/api/v1/revision/decks/${id}/`);
    },
    
    async createDeck(data) {
        return await window.apiService.request('/api/v1/revision/decks/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateDeck(id, data) {
        return await window.apiService.request(`/api/v1/revision/decks/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },
    
    async deleteDeck(id) {
        return await window.apiService.request(`/api/v1/revision/decks/${id}/`, {
            method: 'DELETE'
        });
    },
    
    async getStats() {
        return await window.apiService.request('/api/v1/revision/decks/stats/');
    },
    
    async importDeck(formData) {
        return await window.apiService.request('/api/v1/revision/import/', {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    },
    
    async createCard(deckId, cardData) {
        return await window.apiService.request('/api/v1/revision/flashcards/', {
            method: 'POST',
            body: JSON.stringify({
                deck: deckId,
                ...cardData
            })
        });
    },
    
    async getCards(deckId) {
        // Add timestamp to prevent caching issues
        const timestamp = Date.now();
        return await window.apiService.request(`/api/v1/revision/flashcards/?deck=${deckId}&_t=${timestamp}`);
    },
    
    async updateCard(cardId, cardData) {
        return await window.apiService.request(`/api/v1/revision/flashcards/${cardId}/`, {
            method: 'PATCH',
            body: JSON.stringify(cardData)
        });
    },
    
    async deleteCard(cardId) {
        return await window.apiService.request(`/api/v1/revision/flashcards/${cardId}/`, {
            method: 'DELETE'
        });
    }
};

// Utility functions
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

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function calculateProgress(deck) {
    if (!deck.cards_count || deck.cards_count === 0) return 0;
    return Math.round((deck.learned_count || 0) / deck.cards_count * 100);
}

// Core functions
async function loadDecks(reset = true) {
    try {
        if (reset) {
            appState.currentPage = 1;
            appState.decks = [];
            const emptyElement = document.getElementById('decksEmpty');
            if (emptyElement) emptyElement.style.display = 'none';
        }
        
        appState.isLoading = true;
        
        const [decksResponse, statsResponse] = await Promise.all([
            revisionAPI.getDecks(appState.currentPage, appState.filters),
            revisionAPI.getStats()
        ]);
        
        if (reset) {
            appState.decks = decksResponse.results || [];
        } else {
            appState.decks = [...appState.decks, ...(decksResponse.results || [])];
        }
        
        appState.hasMore = !!decksResponse.next;
        appState.currentPage = decksResponse.next ? appState.currentPage + 1 : appState.currentPage;
        appState.stats = statsResponse;
        
        renderDecksList();
        updateStats();
        
    } catch (error) {
        console.error('Error loading decks:', error);
        window.notificationService.error('Erreur lors du chargement des decks');
    } finally {
        appState.isLoading = false;
    }
}

function updateStats() {
    const stats = appState.stats;
    
    // Detailed stats
    const elements = {
        totalDecks: document.getElementById('totalDecks'),
        totalCards: document.getElementById('totalCards'),
        totalLearned: document.getElementById('totalLearned'),
        completionRate: document.getElementById('completionRate')
    };
    
    if (elements.totalDecks) elements.totalDecks.textContent = stats.totalDecks;
    if (elements.totalCards) elements.totalCards.textContent = stats.totalCards;
    if (elements.totalLearned) elements.totalLearned.textContent = stats.totalLearned;
    if (elements.completionRate) elements.completionRate.textContent = `${stats.completionRate}%`;
}

function renderDecksList() {
    const decksList = document.getElementById('decksList');
    const decksEmpty = document.getElementById('decksEmpty');
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    
    if (!decksList) return;
    
    if (appState.decks.length === 0) {
        decksList.style.display = 'none';
        if (decksEmpty) decksEmpty.style.display = 'block';
        if (loadMoreContainer) loadMoreContainer.style.display = 'none';
        return;
    }
    
    if (decksEmpty) decksEmpty.style.display = 'none';
    decksList.style.display = 'block';
    
    decksList.innerHTML = appState.decks.map(deck => {
        const progress = calculateProgress(deck);
        return `
        <li class="deck-item ${appState.selectedDeck?.id === deck.id ? 'active' : ''}" 
            onclick="selectDeck(${deck.id})">
            <div class="deck-header">
                <div class="deck-name">${deck.name || 'Sans nom'}</div>
                <div class="deck-stats">
                    <span class="deck-badge">${deck.cards_count || 0}</span>
                    ${deck.is_public ? '<i class="bi bi-globe2" title="Public"></i>' : ''}
                    ${deck.is_archived ? '<i class="bi bi-archive" title="Archivé"></i>' : ''}
                </div>
            </div>
            <div class="deck-description">${deck.description || 'Aucune description'}</div>
            <div class="deck-meta">
                <div class="deck-progress">
                    <span>${deck.learned_count || 0}/${deck.cards_count || 0}</span>
                    <div class="progress-bar-custom">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span>${progress}%</span>
                </div>
                <span>${formatDate(deck.updated_at)}</span>
            </div>
        </li>
    `;
    }).join('');
    
    // Load more button
    if (loadMoreContainer) {
        loadMoreContainer.style.display = appState.hasMore ? 'block' : 'none';
    }
}

// UI Management Functions
async function selectDeck(deckId) {
    try {
        const deck = await revisionAPI.getDeck(deckId);
        appState.selectedDeck = deck;
        
        // Hide all other sections first
        const elements = getElements();
        elements.welcomeState.style.display = 'none';
        elements.deckDetails.style.display = 'block';
        elements.createDeckForm.style.display = 'none';
        elements.importDeckForm.style.display = 'none';
        elements.createCardForm.style.display = 'none';
        elements.viewAllCardsSection.style.display = 'none';
        elements.editCardForm.style.display = 'none';
        
        // Populate deck details
        elements.deckName.textContent = deck.name || 'Sans nom';
        elements.deckDescription.textContent = deck.description || 'Aucune description';
        
        const progress = calculateProgress(deck);
        elements.deckProgress.textContent = `${deck.learned_count || 0}/${deck.cards_count || 0}`;
        elements.deckProgressBar.style.width = `${progress}%`;
        
        // Update decks list visual state
        renderDecksList();
        
        // Hide sidebar on mobile
        if (window.innerWidth < 768) {
            elements.sidebar.classList.remove('show');
        }
        
    } catch (error) {
        console.error('Error loading deck:', error);
        window.notificationService.error('Erreur lors du chargement du deck');
    }
}

function showCreateForm() {
    const elements = getElements();
    elements.welcomeState.style.display = 'none';
    elements.deckDetails.style.display = 'none';
    elements.createDeckForm.style.display = 'block';
    elements.importDeckForm.style.display = 'none';
    
    // Clear form
    elements.newDeckName.value = '';
    elements.newDeckDescription.value = '';
    elements.newDeckVisibility.value = 'private';
    
    // Focus on name input
    elements.newDeckName.focus();
}

function hideCreateForm() {
    const elements = getElements();
    elements.createDeckForm.style.display = 'none';
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

function showImportForm() {
    const elements = getElements();
    elements.welcomeState.style.display = 'none';
    elements.deckDetails.style.display = 'none';
    elements.createDeckForm.style.display = 'none';
    elements.importDeckForm.style.display = 'block';
    
    // Clear form
    elements.importFile.value = '';
    elements.importDeckName.value = '';
}

function hideImportForm() {
    const elements = getElements();
    elements.importDeckForm.style.display = 'none';
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

function showCreateCardForm() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Veuillez sélectionner un deck d\'abord');
        return;
    }
    
    const elements = getElements();
    elements.welcomeState.style.display = 'none';
    elements.deckDetails.style.display = 'none';
    elements.createDeckForm.style.display = 'none';
    elements.importDeckForm.style.display = 'none';
    elements.createCardForm.style.display = 'block';
    
    // Clear form
    elements.newCardFront.value = '';
    elements.newCardBack.value = '';
    
    // Focus on front input
    elements.newCardFront.focus();
}

function hideCreateCardForm() {
    const elements = getElements();
    elements.createCardForm.style.display = 'none';
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

async function createNewCard() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    const elements = getElements();
    const frontText = elements.newCardFront.value.trim();
    const backText = elements.newCardBack.value.trim();
    
    if (!frontText) {
        window.notificationService.error('Le texte recto est requis');
        elements.newCardFront.focus();
        return;
    }
    
    if (!backText) {
        window.notificationService.error('Le texte verso est requis');
        elements.newCardBack.focus();
        return;
    }
    
    try {
        const cardData = {
            front_text: frontText,
            back_text: backText
        };
        
        const newCard = await revisionAPI.createCard(appState.selectedDeck.id, cardData);
        
        window.notificationService.success('Carte créée avec succès');
        
        // Close form first
        hideCreateCardForm();
        
        // Reload everything to get fresh data
        await Promise.all([
            loadDecks(), // Reload deck list with updated counts
            selectDeck(appState.selectedDeck.id) // Reload selected deck details
        ]);
        
    } catch (error) {
        console.error('Error creating card:', error);
        window.notificationService.error('Erreur lors de la création de la carte');
    }
}

async function viewAllCards() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Veuillez sélectionner un deck d\'abord');
        return;
    }
    
    try {
        // Hide other sections
        const elements = getElements();
        elements.welcomeState.style.display = 'none';
        elements.deckDetails.style.display = 'none';
        elements.createDeckForm.style.display = 'none';
        elements.importDeckForm.style.display = 'none';
        elements.createCardForm.style.display = 'none';
        elements.editCardForm.style.display = 'none';
        elements.viewAllCardsSection.style.display = 'block';
        
        // Set deck name
        elements.deckNameInCards.textContent = appState.selectedDeck.name;
        
        // Load cards for the current deck
        await loadDeckCards();
        
    } catch (error) {
        console.error('Error viewing cards:', error);
        window.notificationService.error('Erreur lors du chargement des cartes');
    }
}

async function loadDeckCards() {
    if (!appState.selectedDeck) {
        console.error('No deck selected');
        return;
    }
    
    const deckId = appState.selectedDeck.id;
    console.log(`Loading cards for deck ${deckId}: ${appState.selectedDeck.name}`);
    
    try {
        if (appState.isLoadingCards) {
            console.log('Already loading cards, skipping...');
            return;
        }
        
        appState.isLoadingCards = true;
        const elements = getElements();
        const response = await revisionAPI.getCards(deckId);
        
        console.log(`API response for deck ${deckId}:`, response);
        
        // Handle both paginated response and direct array response
        const cards = response.results || response || [];
        
        // Filter cards to only show those belonging to the current deck
        const filteredCards = cards.filter(card => card.deck === deckId);
        
        console.log(`Found ${filteredCards.length} cards for deck ${deckId}`);
        
        if (!filteredCards || filteredCards.length === 0) {
            elements.cardsContainer.style.display = 'none';
            elements.noCardsMessage.style.display = 'block';
            return;
        }
        
        elements.noCardsMessage.style.display = 'none';
        elements.cardsContainer.style.display = 'block';
        
        // Render cards with deck ID for debugging
        elements.cardsContainer.innerHTML = filteredCards.map(card => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-muted">Recto</h6>
                            <p class="card-text">${card.front_text}</p>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-muted">Verso</h6>
                            <p class="card-text">${card.back_text}</p>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div>
                            <span class="badge ${card.learned ? 'bg-success' : 'bg-secondary'}">
                                ${card.learned ? 'Apprise' : 'À apprendre'}
                            </span>
                            <small class="text-muted ms-2">
                                Créée le ${formatDate(card.created_at)}
                            </small>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="window.revisionMain.editCard(${card.id})" title="Modifier">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="window.revisionMain.deleteCard(${card.id})" title="Supprimer">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading deck cards:', error);
        window.notificationService.error('Erreur lors du chargement des cartes');
    } finally {
        appState.isLoadingCards = false;
    }
}

function backToDeckView() {
    const elements = getElements();
    elements.viewAllCardsSection.style.display = 'none';
    elements.editCardForm.style.display = 'none';
    
    // Clear cards container to prevent showing wrong cards
    if (elements.cardsContainer) {
        elements.cardsContainer.innerHTML = '';
    }
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

// Card management functions
async function editCard(cardId) {
    try {
        // Get current card data
        const response = await revisionAPI.getCards(appState.selectedDeck.id);
        const cards = response.results || response || [];
        const card = cards.find(c => c.id === cardId);
        
        if (!card) {
            window.notificationService.error('Carte introuvable - elle a peut-être été supprimée');
            // Refresh the cards view
            await loadDeckCards();
            return;
        }
        
        // Show edit form
        const elements = getElements();
        elements.editCardId.value = cardId;
        elements.editCardFront.value = card.front_text;
        elements.editCardBack.value = card.back_text;
        
        // Hide other sections and show edit form
        elements.viewAllCardsSection.style.display = 'none';
        elements.editCardForm.style.display = 'block';
        
        // Focus on front text
        elements.editCardFront.focus();
        
    } catch (error) {
        console.error('Error loading card for edit:', error);
        
        if (error.status === 404) {
            window.notificationService.error('Cette carte n\'existe plus');
            await loadDeckCards(); // Refresh view
        } else {
            window.notificationService.error('Erreur lors du chargement de la carte');
        }
    }
}

function hideEditCardForm() {
    const elements = getElements();
    elements.editCardForm.style.display = 'none';
    elements.viewAllCardsSection.style.display = 'block';
    
    // Clear form data
    elements.editCardId.value = '';
    elements.editCardFront.value = '';
    elements.editCardBack.value = '';
}

async function submitCardEdit() {
    const elements = getElements();
    const cardId = parseInt(elements.editCardId.value);
    const frontText = elements.editCardFront.value.trim();
    const backText = elements.editCardBack.value.trim();
    
    if (!frontText) {
        window.notificationService.error('Le texte recto est requis');
        elements.editCardFront.focus();
        return;
    }
    
    if (!backText) {
        window.notificationService.error('Le texte verso est requis');
        elements.editCardBack.focus();
        return;
    }
    
    try {
        // Update card
        await revisionAPI.updateCard(cardId, {
            front_text: frontText,
            back_text: backText
        });
        
        window.notificationService.success('Carte modifiée avec succès');
        
        // Hide form and reload cards
        hideEditCardForm();
        await loadDeckCards();
        
    } catch (error) {
        console.error('Error updating card:', error);
        
        if (error.status === 404) {
            window.notificationService.error('Cette carte n\'existe plus et ne peut pas être modifiée');
            hideEditCardForm();
            await loadDeckCards(); // Refresh view
        } else if (error.status === 403) {
            window.notificationService.error('Vous n\'avez pas l\'autorisation de modifier cette carte');
        } else {
            window.notificationService.error('Erreur lors de la modification de la carte');
        }
    }
}

async function deleteCard(cardId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette carte ?')) return;
    
    try {
        await revisionAPI.deleteCard(cardId);
        
        window.notificationService.success('Carte supprimée avec succès');
        
        // Sequential reload to avoid conflicts
        await loadDeckCards(); // Reload cards view first
        await loadDecks(); // Then update deck counts
        
        // If in deck details view, update that too
        if (appState.selectedDeck) {
            const freshDeck = await revisionAPI.getDeck(appState.selectedDeck.id);
            appState.selectedDeck = freshDeck;
            
            const elements = getElements();
            const progress = calculateProgress(freshDeck);
            elements.deckProgress.textContent = `${freshDeck.learned_count || 0}/${freshDeck.cards_count || 0}`;
            elements.deckProgressBar.style.width = `${progress}%`;
        }
        
    } catch (error) {
        console.error('Error deleting card:', error);
        
        // Handle specific error cases
        if (error.status === 404) {
            window.notificationService.warning('Cette carte a déjà été supprimée');
            // Reload the view to reflect current state
            await loadDeckCards();
            await loadDecks();
        } else if (error.status === 403) {
            window.notificationService.error('Vous n\'avez pas l\'autorisation de supprimer cette carte');
        } else {
            window.notificationService.error('Erreur lors de la suppression de la carte');
        }
    }
}

async function createNewDeck() {
    const elements = getElements();
    const name = elements.newDeckName.value.trim();
    const description = elements.newDeckDescription.value.trim();
    const isPublic = elements.newDeckVisibility.value === 'public';
    
    if (!name) {
        window.notificationService.error('Le nom du deck est requis');
        return;
    }
    
    try {
        const deckData = {
            name: name,
            description: description,
            is_public: isPublic
        };
        
        const newDeck = await revisionAPI.createDeck(deckData);
        
        window.notificationService.success('Deck créé avec succès');
        
        // Reload decks and select the new one
        await loadDecks();
        await selectDeck(newDeck.id);
        
    } catch (error) {
        console.error('Error creating deck:', error);
        window.notificationService.error('Erreur lors de la création du deck');
    }
}

async function importNewDeck() {
    const elements = getElements();
    const file = elements.importFile.files[0];
    const name = elements.importDeckName.value.trim();
    
    if (!file) {
        window.notificationService.error('Veuillez sélectionner un fichier');
        return;
    }
    
    if (!name) {
        window.notificationService.error('Le nom du deck est requis');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        
        const newDeck = await revisionAPI.importDeck(formData);
        
        window.notificationService.success('Deck importé avec succès');
        
        // Reload decks and select the new one
        await loadDecks();
        await selectDeck(newDeck.id);
        
    } catch (error) {
        console.error('Error importing deck:', error);
        window.notificationService.error('Erreur lors de l\'importation du deck');
    }
}

// Filter functions
function handleSearch() {
    const elements = getElements();
    appState.filters.search = elements.searchInput.value;
    loadDecks();
}

function handleStatusFilter() {
    const elements = getElements();
    appState.filters.status = elements.statusFilter.value;
    loadDecks();
}

function handleSortFilter() {
    const elements = getElements();
    appState.filters.sort = elements.sortFilter.value;
    loadDecks();
}

function loadMoreDecks() {
    if (!appState.isLoading && appState.hasMore) {
        loadDecks(false);
    }
}

// UI functions
function toggleSidebar() {
    const elements = getElements();
    elements.sidebar.classList.toggle('show');
}

function backToList() {
    const elements = getElements();
    elements.sidebar.classList.add('show');
}

// Helper function to get DOM elements
function getElements() {
    return {
        // Sidebar
        sidebar: document.getElementById('revisionSidebar'),
        toggleSidebar: document.getElementById('toggleSidebar'),
        decksList: document.getElementById('decksList'),
        decksEmpty: document.getElementById('decksEmpty'),
        loadMoreContainer: document.getElementById('loadMoreContainer'),
        loadMoreBtn: document.getElementById('loadMoreBtn'),
        
        // Filters
        searchInput: document.getElementById('searchInput'),
        statusFilter: document.getElementById('statusFilter'),
        sortFilter: document.getElementById('sortFilter'),
        
        // Study area
        welcomeState: document.getElementById('welcomeState'),
        deckDetails: document.getElementById('deckDetails'),
        createDeckForm: document.getElementById('createDeckForm'),
        importDeckForm: document.getElementById('importDeckForm'),
        createCardForm: document.getElementById('createCardForm'),
        viewAllCardsSection: document.getElementById('viewAllCardsSection'),
        
        // Deck details
        deckName: document.getElementById('deckName'),
        deckDescription: document.getElementById('deckDescription'),
        deckProgress: document.getElementById('deckProgress'),
        deckProgressBar: document.getElementById('deckProgressBar'),
        
        // Create form
        newDeckName: document.getElementById('newDeckName'),
        newDeckDescription: document.getElementById('newDeckDescription'),
        newDeckVisibility: document.getElementById('newDeckVisibility'),
        
        // Import form
        importFile: document.getElementById('importFile'),
        importDeckName: document.getElementById('importDeckName'),
        
        // Create card form
        newCardFront: document.getElementById('newCardFront'),
        newCardBack: document.getElementById('newCardBack'),
        
        // Buttons
        createDeck: document.getElementById('createDeck'),
        importDeck: document.getElementById('importDeck'),
        refreshDecks: document.getElementById('refreshDecks'),
        backToList: document.getElementById('backToList'),
        addCard: document.getElementById('addCard'),
        viewAllCards: document.getElementById('viewAllCards'),
        backToDeckView: document.getElementById('backToDeckView'),
        submitCreate: document.getElementById('submitCreate'),
        cancelCreate: document.getElementById('cancelCreate'),
        cancelCreateAlt: document.getElementById('cancelCreateAlt'),
        submitImport: document.getElementById('submitImport'),
        cancelImport: document.getElementById('cancelImport'),
        cancelImportAlt: document.getElementById('cancelImportAlt'),
        submitCardCreate: document.getElementById('submitCardCreate'),
        cancelCardCreate: document.getElementById('cancelCardCreate'),
        cancelCardCreateAlt: document.getElementById('cancelCardCreateAlt'),
        
        // Stats
        totalDecks: document.getElementById('totalDecks'),
        totalCards: document.getElementById('totalCards'),
        totalLearned: document.getElementById('totalLearned'),
        completionRate: document.getElementById('completionRate'),
        
        // Cards view
        deckNameInCards: document.getElementById('deckNameInCards'),
        cardsContainer: document.getElementById('cardsContainer'),
        noCardsMessage: document.getElementById('noCardsMessage'),
        
        // Edit card form
        editCardForm: document.getElementById('editCardForm'),
        editCardId: document.getElementById('editCardId'),
        editCardFront: document.getElementById('editCardFront'),
        editCardBack: document.getElementById('editCardBack'),
        submitCardEdit: document.getElementById('submitCardEdit'),
        cancelCardEdit: document.getElementById('cancelCardEdit'),
        cancelCardEditAlt: document.getElementById('cancelCardEditAlt')
    };
}

// Setup event listeners
function setupEventListeners() {
    const elements = getElements();
    
    // Sidebar toggle
    elements.toggleSidebar?.addEventListener('click', toggleSidebar);
    
    // Search and filters
    elements.searchInput?.addEventListener('input', debounce(handleSearch, 300));
    elements.statusFilter?.addEventListener('change', handleStatusFilter);
    elements.sortFilter?.addEventListener('change', handleSortFilter);
    
    // Buttons
    elements.createDeck?.addEventListener('click', showCreateForm);
    elements.importDeck?.addEventListener('click', showImportForm);
    elements.refreshDecks?.addEventListener('click', loadDecks);
    elements.backToList?.addEventListener('click', backToList);
    elements.addCard?.addEventListener('click', showCreateCardForm);
    elements.viewAllCards?.addEventListener('click', viewAllCards);
    elements.backToDeckView?.addEventListener('click', backToDeckView);
    
    // Create form
    elements.submitCreate?.addEventListener('click', createNewDeck);
    elements.cancelCreate?.addEventListener('click', hideCreateForm);
    elements.cancelCreateAlt?.addEventListener('click', hideCreateForm);
    
    // Import form
    elements.submitImport?.addEventListener('click', importNewDeck);
    elements.cancelImport?.addEventListener('click', hideImportForm);
    elements.cancelImportAlt?.addEventListener('click', hideImportForm);
    
    // Create card form
    elements.submitCardCreate?.addEventListener('click', createNewCard);
    elements.cancelCardCreate?.addEventListener('click', hideCreateCardForm);
    elements.cancelCardCreateAlt?.addEventListener('click', hideCreateCardForm);
    
    // Edit card form
    elements.submitCardEdit?.addEventListener('click', submitCardEdit);
    elements.cancelCardEdit?.addEventListener('click', hideEditCardForm);
    elements.cancelCardEditAlt?.addEventListener('click', hideEditCardForm);
    
    // Create deck buttons
    document.querySelectorAll('.create-deck-btn').forEach(btn => {
        btn.addEventListener('click', showCreateForm);
    });
    
    // Load more
    elements.loadMoreBtn?.addEventListener('click', loadMoreDecks);
}

// Initialize the app
function initializeApp() {
    setupEventListeners();
    loadDecks();
}

// Export for global access
window.revisionMain = {
    loadDecks,
    appState,
    revisionAPI,
    updateStats,
    renderDecksList,
    formatDate,
    calculateProgress,
    debounce,
    selectDeck,
    showCreateForm,
    hideCreateForm,
    showImportForm,
    hideImportForm,
    showCreateCardForm,
    hideCreateCardForm,
    createNewDeck,
    createNewCard,
    importNewDeck,
    viewAllCards,
    loadDeckCards,
    backToDeckView,
    editCard,
    deleteCard,
    submitCardEdit,
    hideEditCardForm,
    handleSearch,
    handleStatusFilter,
    handleSortFilter,
    loadMoreDecks,
    toggleSidebar,
    backToList,
    setupEventListeners,
    initializeApp,
    getElements
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);