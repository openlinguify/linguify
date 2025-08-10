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
        sort: 'updated_desc',
        tags: []
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
    
    async previewImport(deckId, formData) {
        // Pour FormData, on doit gérer les headers différemment
        const csrfToken = window.apiService.getCSRFToken();
        return await fetch(`/api/v1/revision/decks/${deckId}/import/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        }).then(async response => {
            if (!response.ok) {
                let errorMessage = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData.detail) errorMessage = errorData.detail;
                } catch (e) {}
                const error = new Error(errorMessage);
                error.status = response.status;
                throw error;
            }
            return response.json();
        });
    },

    async importDeck(deckId, formData) {
        // Pour FormData, on doit gérer les headers différemment
        const csrfToken = window.apiService.getCSRFToken();
        return await fetch(`/api/v1/revision/decks/${deckId}/import/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
                // Ne PAS définir Content-Type, le navigateur le fera automatiquement avec boundary
            }
        }).then(async response => {
            if (!response.ok) {
                let errorMessage = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData.detail) errorMessage = errorData.detail;
                } catch (e) {}
                const error = new Error(errorMessage);
                error.status = response.status;
                throw error;
            }
            return response.json();
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
    },
    
    async getLearningSettings(deckId) {
        return await window.apiService.request(`/api/v1/revision/decks/${deckId}/learning_settings/`);
    },
    
    async updateLearningSettings(deckId, settings) {
        return await window.apiService.request(`/api/v1/revision/decks/${deckId}/learning_settings/`, {
            method: 'PATCH',
            body: JSON.stringify(settings)
        });
    },
    
    async applyPreset(deckId, presetName) {
        return await window.apiService.request(`/api/v1/revision/decks/${deckId}/apply_preset/`, {
            method: 'POST',
            body: JSON.stringify({ preset_name: presetName })
        });
    },
    
    async updateCardProgress(cardId, isCorrect) {
        return await window.apiService.request(`/api/v1/revision/flashcards/${cardId}/update_review_progress/`, {
            method: 'POST',
            body: JSON.stringify({ is_correct: isCorrect })
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
    
    // Apply client-side tags filtering
    let filteredDecks = appState.decks;
    if (appState.filters.tags && appState.filters.tags.length > 0) {
        filteredDecks = window.filterDecksByTags ? 
            window.filterDecksByTags(appState.decks, appState.filters.tags) : 
            appState.decks;
    }
    
    decksList.innerHTML = filteredDecks.map(deck => {
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
            <div class="deck-tags-container">
                <div class="deck-tags">${window.displayDeckTags ? window.displayDeckTags(deck) : ''}</div>
                <button class="btn-add-tag" onclick="event.stopPropagation(); quickEditTags(${deck.id})" title="Ajouter des tags">
                    <i class="bi bi-tag"></i>
                </button>
            </div>
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

// Central function to hide all sections
function hideAllSections() {
    const elements = getElements();
    
    // Main sections
    if (elements.welcomeState) elements.welcomeState.style.display = 'none';
    if (elements.deckDetails) elements.deckDetails.style.display = 'none';
    if (elements.createDeckForm) elements.createDeckForm.style.display = 'none';
    if (elements.editDeckForm) elements.editDeckForm.style.display = 'none';
    if (elements.importDeckForm) elements.importDeckForm.style.display = 'none';
    if (elements.importPreviewSection) elements.importPreviewSection.style.display = 'none';
    if (elements.createCardForm) elements.createCardForm.style.display = 'none';
    if (elements.editCardForm) elements.editCardForm.style.display = 'none';
    
    // Study modes
    if (elements.flashcardStudyMode) elements.flashcardStudyMode.style.display = 'none';
    if (elements.quizStudyMode) elements.quizStudyMode.style.display = 'none';
    if (elements.matchingStudyMode) elements.matchingStudyMode.style.display = 'none';
    if (elements.spacedStudyMode) elements.spacedStudyMode.style.display = 'none';
}

// UI Management Functions
async function selectDeck(deckId) {
    try {
        const deck = await revisionAPI.getDeck(deckId);
        appState.selectedDeck = deck;
        
        // Hide all sections first
        hideAllSections();
        
        // Show deck details
        const elements = getElements();
        elements.deckDetails.style.display = 'block';
        
        // Populate deck details
        elements.deckName.textContent = deck.name || 'Sans nom';
        elements.deckDescription.textContent = deck.description || 'Aucune description';
        
        // Display deck tags
        const deckTagsDisplay = document.getElementById('deckTagsDisplay');
        if (deckTagsDisplay && window.displayDeckTags) {
            deckTagsDisplay.innerHTML = window.displayDeckTags(deck);
        }
        
        const progress = calculateProgress(deck);
        elements.deckProgress.textContent = `${deck.learned_count || 0}/${deck.cards_count || 0}`;
        elements.deckProgressBar.style.width = `${progress}%`;
        
        // Initialize tags manager for deck details if available
        if (window.tagsManager && elements.editDeckTagsInput && elements.editDeckTagsDisplay) {
            if (!window.tagsManager.isInitialized) {
                window.tagsManager.init('editDeckTagsInput', 'editDeckTagsDisplay');
            }
            // Set the current deck's tags in the manager
            window.tagsManager.setTags(deck.tags || []);
        }
        
        // Update decks list visual state
        renderDecksList();
        
        // Update archive button text and icon based on deck status
        updateArchiveButton();
        
        // Load cards automatically
        await loadDeckCards();
        
        // Update cards count
        updateCardsCount();
        
        // Show language settings if deck has cards
        showDeckLanguageSettings(deck);
        
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
    hideAllSections();
    
    const elements = getElements();
    elements.createDeckForm.style.display = 'block';
    
    // Clear form
    elements.newDeckName.value = '';
    elements.newDeckDescription.value = '';
    elements.newDeckVisibility.value = 'private';
    
    // Initialize tags manager for create form
    if (window.tagsManager && !window.tagsManager.isInitialized) {
        window.tagsManager.init('newDeckTagsInput', 'newDeckTagsDisplay');
    }
    if (window.tagsManager) {
        window.tagsManager.setTags([]);
    }
    
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
    hideAllSections();
    
    const elements = getElements();
    elements.importDeckForm.style.display = 'block';
    
    // Clear form
    elements.importFile.value = '';
    elements.importDeckName.value = '';
    
    // Reset form state
    clearSelectedFile();
    updateImportButton();
    
    // Initialize drag and drop
    initializeDragAndDrop();
    
    // Initialize real-time validation
    initializeRealTimeValidation();
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
    
    hideAllSections();
    
    const elements = getElements();
    elements.createCardForm.style.display = 'block';
    
    // Clear form and apply defaults
    elements.newCardFront.value = '';
    elements.newCardBack.value = '';
    
    // Apply default languages if set
    const frontLangDefault = appState.deckDefaults?.frontLanguage || '';
    const backLangDefault = appState.deckDefaults?.backLanguage || '';
    
    document.getElementById('newCardFrontLang').value = frontLangDefault;
    document.getElementById('newCardBackLang').value = backLangDefault;
    
    // Focus on front input
    elements.newCardFront.focus();
}

function hideCreateCardForm() {
    const elements = getElements();
    elements.createCardForm.style.display = 'none';
    
    // Clear form fields
    elements.newCardFront.value = '';
    elements.newCardBack.value = '';
    document.getElementById('newCardFrontLang').value = '';
    document.getElementById('newCardBackLang').value = '';
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
    
    // Reset language selectors to default state
    resetLanguageSelectors();
}

// Functions to handle language selector visibility
function toggleFrontLanguageSelector() {
    const selector = document.getElementById('frontLangSelector');
    const button = document.getElementById('changeFrontLang');
    
    if (selector && button) {
        if (selector.style.display === 'none' || selector.style.display === '') {
            selector.style.display = 'block';
            button.innerHTML = '<i class="bi bi-check" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">Confirmer</span>';
            button.title = 'Confirmer le choix de langue';
        } else {
            selector.style.display = 'none';
            button.innerHTML = '<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">Modifier</span>';
            button.title = 'Modifier la langue pour cette carte';
            updateLanguageDisplay('front');
        }
    }
}

function toggleBackLanguageSelector() {
    const selector = document.getElementById('backLangSelector');
    const button = document.getElementById('changeBackLang');
    
    if (selector && button) {
        if (selector.style.display === 'none' || selector.style.display === '') {
            selector.style.display = 'block';
            button.innerHTML = '<i class="bi bi-check" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">Confirmer</span>';
            button.title = 'Confirmer le choix de langue';
        } else {
            selector.style.display = 'none';
            button.innerHTML = '<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">Modifier</span>';
            button.title = 'Modifier la langue pour cette carte';
            updateLanguageDisplay('back');
        }
    }
}

function updateLanguageDisplay(side) {
    const select = document.getElementById(side === 'front' ? 'newCardFrontLang' : 'newCardBackLang');
    const display = document.getElementById(side === 'front' ? 'deckFrontLangDisplay' : 'deckBackLangDisplay');
    
    if (select && display) {
        const selectedOption = select.options[select.selectedIndex];
        if (selectedOption.value === '' || selectedOption.value === null) {
            display.textContent = 'Langue par défaut du deck';
        } else {
            display.textContent = selectedOption.textContent;
        }
    }
}

function resetLanguageSelectors() {
    // Reset front language selector
    const frontSelector = document.getElementById('frontLangSelector');
    const frontButton = document.getElementById('changeFrontLang');
    const frontDisplay = document.getElementById('deckFrontLangDisplay');
    
    if (frontSelector) frontSelector.style.display = 'none';
    if (frontButton) {
        frontButton.innerHTML = '<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">Modifier</span>';
        frontButton.title = 'Modifier la langue pour cette carte';
    }
    if (frontDisplay) frontDisplay.textContent = 'Langue par défaut du deck';
    
    // Reset back language selector
    const backSelector = document.getElementById('backLangSelector');
    const backButton = document.getElementById('changeBackLang');
    const backDisplay = document.getElementById('deckBackLangDisplay');
    
    if (backSelector) backSelector.style.display = 'none';
    if (backButton) {
        backButton.innerHTML = '<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">Modifier</span>';
        backButton.title = 'Modifier la langue pour cette carte';
    }
    if (backDisplay) backDisplay.textContent = 'Langue par défaut du deck';
}

async function createNewCard() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    const elements = getElements();
    const frontText = elements.newCardFront.value.trim();
    const backText = elements.newCardBack.value.trim();
    const frontLang = document.getElementById('newCardFrontLang').value;
    const backLang = document.getElementById('newCardBackLang').value;
    
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
            back_text: backText,
            front_language: frontLang || null,
            back_language: backLang || null
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
                            <span class="badge ${card.learned ? 'bg-linguify-accent' : 'bg-secondary'}">
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
    elements.editCardForm.style.display = 'none';
    
    // Show deck details with cards
    if (appState.selectedDeck) {
        selectDeck(appState.selectedDeck.id);
    } else {
        hideAllSections();
        elements.welcomeState.style.display = 'block';
    }
}

// Study mode functions
function startFlashcardsMode() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Veuillez sélectionner un deck d\'abord');
        return;
    }
    
    if (window.flashcardMode) {
        window.flashcardMode.startStudy(appState.selectedDeck);
    } else {
        window.notificationService.error('Mode Flashcards non disponible');
    }
}

function startLearnMode() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Veuillez sélectionner un deck d\'abord');
        return;
    }
    
    if (window.quizMode) {
        window.quizMode.startQuiz(appState.selectedDeck);
    } else {
        window.notificationService.error('Mode Questionnaire non disponible');
    }
}

function startMatchMode() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Veuillez sélectionner un deck d\'abord');
        return;
    }
    
    if (window.matchingMode) {
        window.matchingMode.startMatching(appState.selectedDeck);
    } else {
        window.notificationService.error('Mode Associer non disponible');
    }
}

function startReviewMode() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Veuillez sélectionner un deck d\'abord');
        return;
    }
    
    if (window.spacedMode) {
        window.spacedMode.startSpacedReview(appState.selectedDeck);
    } else {
        window.notificationService.error('Mode Révision rapide non disponible');
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
        hideAllSections();
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
    
    // Clear form data
    elements.editCardId.value = '';
    elements.editCardFront.value = '';
    elements.editCardBack.value = '';
    
    // Return to deck view with cards
    if (appState.selectedDeck) {
        selectDeck(appState.selectedDeck.id);
    }
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
            is_public: isPublic,
            tags: window.tagsManager ? window.tagsManager.getTags() : []
        };
        
        console.log('Creating deck with data:', deckData);
        console.log('CSRF Token:', window.apiService.getCSRFToken());
        console.log('User authenticated:', window.USER_DATA?.is_authenticated);
        
        const newDeck = await revisionAPI.createDeck(deckData);
        
        window.notificationService.success('Deck créé avec succès');
        
        // Reload decks and select the new one
        await loadDecks();
        await selectDeck(newDeck.id);
        
    } catch (error) {
        console.error('Error creating deck:', error);
        console.error('Error details:', error.data);
        
        // Try to show more specific error message
        if (error.data && error.data.detail) {
            window.notificationService.error(error.data.detail);
        } else if (error.data && error.data.name && error.data.name[0]) {
            window.notificationService.error(error.data.name[0]);
        } else {
            window.notificationService.error('Erreur lors de la création du deck');
        }
    }
}

// Variables globales pour l'import
let importState = {
    file: null,
    deckName: '',
    previewData: null,
    columns: null,
    tempDeck: null
};

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
        // Stocker les infos pour l'étape suivante
        importState.file = file;
        importState.deckName = name;
        
        // First, create the deck
        const deckData = {
            name: name,
            description: `Deck importé depuis ${file.name}`,
            is_public: false
        };
        
        const newDeck = await revisionAPI.createDeck(deckData);
        importState.tempDeck = newDeck;
        
        // Then, get preview of the file
        const formData = new FormData();
        formData.append('file', file);
        formData.append('has_header', 'true'); // Initial load always with header
        formData.append('preview_only', 'true');
        formData.append('front_column', '0');
        formData.append('back_column', '1');
        
        const previewResult = await revisionAPI.previewImport(newDeck.id, formData);
        importState.previewData = previewResult.preview || [];
        importState.columns = previewResult.columns || [];
        
        // Show preview step
        showImportPreview(previewResult);
        
    } catch (error) {
        console.error('Erreur lors du preview:', error);
        
        // Gérer les erreurs spécifiques
        if (error.status === 400 && error.message.includes('deck with this name already exists')) {
            window.notificationService.error('Un deck avec ce nom existe déjà. Veuillez choisir un autre nom.');
        } else {
            window.notificationService.error('Erreur lors de la préparation de l\'import: ' + error.message);
        }
    }
}

// ===== FONCTIONS D'INTERACTIVITÉ AVANCÉE =====

function initializeDragAndDrop() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('importFile');
    
    if (!dropZone || !fileInput) return;
    
    // Prévenir les comportements par défaut
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle click on drop zone
    dropZone.addEventListener('click', () => fileInput.click());
    
    // Handle file input change
    fileInput.addEventListener('change', handleFileSelect, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        dropZone.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect({ target: { files } });
        }
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    
    if (!file) {
        clearSelectedFile();
        return;
    }
    
    // Validation du fichier
    if (!validateFile(file)) {
        clearSelectedFile();
        return;
    }
    
    // Afficher les informations du fichier
    showSelectedFileInfo(file);
    updateImportButton();
}

function validateFile(file) {
    const allowedTypes = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
    ];
    
    const allowedExtensions = ['.xls', '.xlsx', '.csv'];
    
    // Vérifier le type MIME
    if (!allowedTypes.includes(file.type)) {
        // Fallback: vérifier l'extension
        const hasValidExtension = allowedExtensions.some(ext => 
            file.name.toLowerCase().endsWith(ext)
        );
        
        if (!hasValidExtension) {
            window.notificationService.error(
                'Format de fichier non supporté. Utilisez .xlsx, .xls ou .csv'
            );
            return false;
        }
    }
    
    // Vérifier la taille (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        window.notificationService.error(
            'Le fichier est trop volumineux. Taille maximum : 10MB'
        );
        return false;
    }
    
    return true;
}

function showSelectedFileInfo(file) {
    const selectedFileInfo = document.getElementById('selectedFileInfo');
    const selectedFileName = document.getElementById('selectedFileName');
    const selectedFileSize = document.getElementById('selectedFileSize');
    
    if (selectedFileInfo && selectedFileName && selectedFileSize) {
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatFileSize(file.size);
        selectedFileInfo.style.display = 'block';
        
        // Animer l'apparition
        selectedFileInfo.style.opacity = '0';
        selectedFileInfo.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            selectedFileInfo.style.transition = 'all 0.3s ease';
            selectedFileInfo.style.opacity = '1';
            selectedFileInfo.style.transform = 'translateY(0)';
        }, 10);
    }
}

function clearSelectedFile() {
    const selectedFileInfo = document.getElementById('selectedFileInfo');
    const fileInput = document.getElementById('importFile');
    
    if (selectedFileInfo) selectedFileInfo.style.display = 'none';
    if (fileInput) fileInput.value = '';
    
    updateImportButton();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function initializeRealTimeValidation() {
    const deckNameInput = document.getElementById('importDeckName');
    
    if (!deckNameInput) return;
    
    // Debounced validation
    let validationTimeout;
    
    deckNameInput.addEventListener('input', function() {
        clearTimeout(validationTimeout);
        
        validationTimeout = setTimeout(() => {
            validateDeckName(this.value.trim());
            updateImportButton();
        }, 300);
    });
    
    // Real-time character counter
    deckNameInput.addEventListener('input', function() {
        updateCharacterCounter(this.value);
    });
}

function validateDeckName(name) {
    const deckNameInput = document.getElementById('importDeckName');
    const errorElement = document.getElementById('deckNameError');
    
    if (!deckNameInput || !errorElement) return false;
    
    // Reset states
    deckNameInput.classList.remove('is-valid', 'is-invalid');
    errorElement.textContent = '';
    
    if (!name) {
        deckNameInput.classList.add('is-invalid');
        errorElement.textContent = 'Le nom du deck est requis';
        return false;
    }
    
    if (name.length < 3) {
        deckNameInput.classList.add('is-invalid');
        errorElement.textContent = 'Le nom doit contenir au moins 3 caractères';
        return false;
    }
    
    if (name.length > 100) {
        deckNameInput.classList.add('is-invalid');
        errorElement.textContent = 'Le nom ne peut pas dépasser 100 caractères';
        return false;
    }
    
    // Vérifier si le nom existe déjà
    const existingDeck = appState.decks.find(deck => 
        deck.name.toLowerCase() === name.toLowerCase()
    );
    
    if (existingDeck) {
        deckNameInput.classList.add('is-invalid');
        errorElement.textContent = 'Un deck avec ce nom existe déjà';
        return false;
    }
    
    deckNameInput.classList.add('is-valid');
    return true;
}

function updateCharacterCounter(value) {
    const maxLength = 100;
    const remaining = maxLength - value.length;
    
    // Vous pouvez ajouter un compteur de caractères si souhaité
    // Pour l'instant, on se contente de la validation
}

function updateImportButton() {
    const submitButton = document.getElementById('submitImport');
    const fileInput = document.getElementById('importFile');
    const deckNameInput = document.getElementById('importDeckName');
    
    if (!submitButton || !fileInput || !deckNameInput) return;
    
    const hasFile = fileInput.files && fileInput.files.length > 0;
    const hasValidName = validateDeckName(deckNameInput.value.trim());
    
    const isValid = hasFile && hasValidName;
    
    submitButton.disabled = !isValid;
    
    if (isValid) {
        submitButton.classList.remove('btn-secondary');
        submitButton.classList.add('btn-gradient');
    } else {
        submitButton.classList.remove('btn-gradient');
        submitButton.classList.add('btn-secondary');
    }
}

function showImportPreview(previewResult) {
    hideAllSections();
    
    const elements = getElements();
    elements.importPreviewSection.style.display = 'block';
    
    // Vérifier que previewResult contient les données attendues
    if (!previewResult || typeof previewResult !== 'object') {
        window.notificationService.error('Données de preview invalides');
        return;
    }
    
    // Afficher les infos du fichier avec animation
    animateValue(elements.previewFileName, importState.file.name);
    animateValue(elements.previewTotalRows, previewResult.total_rows || 0);
    
    // Estimer le nombre de cartes
    const totalRows = previewResult.total_rows || 0;
    const hasHeader = document.getElementById('hasHeaderCheck').checked;
    const estimatedCards = Math.max(0, hasHeader ? totalRows - 1 : totalRows);
    animateValue(document.getElementById('previewEstimatedCards'), estimatedCards);
    
    // Afficher les options de colonnes
    const frontSelect = elements.frontColumnSelect;
    const backSelect = elements.backColumnSelect;
    
    frontSelect.innerHTML = '';
    backSelect.innerHTML = '';
    
    const columns = previewResult.columns || [];
    if (columns.length === 0) {
        window.notificationService.error('Aucune colonne trouvée dans le fichier');
        return;
    }
    
    columns.forEach(col => {
        const optionFront = document.createElement('option');
        optionFront.value = col.index;
        optionFront.textContent = `Colonne ${col.index + 1}: ${col.name || 'Sans nom'}`;
        frontSelect.appendChild(optionFront);
        
        const optionBack = document.createElement('option');
        optionBack.value = col.index;
        optionBack.textContent = `Colonne ${col.index + 1}: ${col.name || 'Sans nom'}`;
        backSelect.appendChild(optionBack);
    });
    
    // Sélectionner les colonnes par défaut
    frontSelect.value = '0';
    backSelect.value = '1';
    
    // Afficher le preview initial avec animation
    updatePreviewDisplay(previewResult.preview || []);
    
    // Animation d'entrée des cartes
    setTimeout(() => {
        const cards = document.querySelectorAll('.preview-cards-grid .card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }, 100);
}

function updatePreviewDisplay(previewData) {
    const elements = getElements();
    const container = elements.previewCardsContainer;
    
    container.innerHTML = previewData.map(card => `
        <div class="card mb-2">
            <div class="card-body p-3">
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="text-muted mb-1">Recto</h6>
                        <p class="mb-0">${card.front_text || ''}</p>
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-muted mb-1">Verso</h6>
                        <p class="mb-0">${card.back_text || ''}</p>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function updatePreview() {
    try {
        const elements = getElements();
        const frontColumn = elements.frontColumnSelect.value;
        const backColumn = elements.backColumnSelect.value;
        
        if (frontColumn === backColumn) {
            window.notificationService.error('Les colonnes recto et verso doivent être différentes');
            return;
        }
        
        // Afficher l'indicateur de chargement
        const updateIndicator = document.getElementById('previewUpdateIndicator');
        if (updateIndicator) {
            updateIndicator.style.display = 'inline-block';
        }
        
        // Récupérer l'état de la checkbox
        const hasHeader = document.getElementById('hasHeaderCheck').checked;
        
        const formData = new FormData();
        formData.append('file', importState.file);
        formData.append('has_header', hasHeader ? 'true' : 'false');
        formData.append('preview_only', 'true');
        formData.append('front_column', frontColumn);
        formData.append('back_column', backColumn);
        
        const previewResult = await revisionAPI.previewImport(importState.tempDeck.id, formData);
        
        console.log('Preview result:', previewResult);
        
        // Animation de sortie des anciennes cartes
        const container = elements.previewCardsContainer;
        const oldCards = container.querySelectorAll('.card');
        
        // Animer la sortie
        oldCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateX(-20px)';
            }, index * 50);
        });
        
        // Attendre que l'animation se termine puis afficher les nouvelles cartes
        setTimeout(() => {
            updatePreviewDisplay(previewResult.preview || []);
            
            // Animation d'entrée des nouvelles cartes
            setTimeout(() => {
                const newCards = container.querySelectorAll('.card');
                newCards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateX(20px)';
                    setTimeout(() => {
                        card.style.transition = 'all 0.4s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateX(0)';
                    }, index * 100);
                });
            }, 50);
        }, 200);
        
        // Cacher l'indicateur de chargement
        setTimeout(() => {
            if (updateIndicator) {
                updateIndicator.style.display = 'none';
            }
        }, 500);
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour du preview:', error);
        window.notificationService.error('Erreur lors de la mise à jour du preview');
        
        // Cacher l'indicateur en cas d'erreur
        const updateIndicator = document.getElementById('previewUpdateIndicator');
        if (updateIndicator) {
            updateIndicator.style.display = 'none';
        }
    }
}

// ===== FONCTIONS UTILITAIRES D'ANIMATION =====

function animateValue(element, value) {
    if (!element) return;
    
    if (typeof value === 'number') {
        animateNumber(element, 0, value, 1000);
    } else {
        animateText(element, value);
    }
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease out)
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        
        const current = Math.floor(start + (end - start) * easedProgress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        } else {
            element.textContent = end;
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function animateText(element, text) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
        element.textContent = text;
        element.style.transition = 'all 0.3s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 150);
}

async function confirmImport() {
    try {
        const elements = getElements();
        const frontColumn = elements.frontColumnSelect.value;
        const backColumn = elements.backColumnSelect.value;
        
        // Récupérer l'état de la checkbox
        const hasHeader = document.getElementById('hasHeaderCheck').checked;
        
        // Récupérer les langues sélectionnées
        const frontLanguage = document.getElementById('frontLanguageSelect').value;
        const backLanguage = document.getElementById('backLanguageSelect').value;
        
        const formData = new FormData();
        formData.append('file', importState.file);
        formData.append('has_header', hasHeader ? 'true' : 'false');
        formData.append('preview_only', 'false');
        formData.append('front_column', frontColumn);
        formData.append('back_column', backColumn);
        
        if (frontLanguage) {
            formData.append('front_language', frontLanguage);
        }
        if (backLanguage) {
            formData.append('back_language', backLanguage);
        }
        
        const importResult = await revisionAPI.importDeck(importState.tempDeck.id, formData);
        
        window.notificationService.success(`Import réussi ! ${importResult.cards_created} cartes créées`);
        
        // Reload decks and select the new one
        await loadDecks();
        await selectDeck(importState.tempDeck.id);
        
        // Reset import state
        importState = {
            file: null,
            deckName: '',
            previewData: null,
            columns: null,
            tempDeck: null
        };
        
    } catch (error) {
        console.error('Erreur lors de l\'import final:', error);
        window.notificationService.error('Erreur lors de l\'import: ' + error.message);
    }
}

function cancelImportPreview() {
    // TODO: Supprimer le deck temporaire créé
    hideImportPreview();
}

function hideImportPreview() {
    const elements = getElements();
    elements.importPreviewSection.style.display = 'none';
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

// ===== FONCTIONS DE GESTION DES DECKS =====

function showEditDeckForm() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    hideAllSections();
    
    const elements = getElements();
    elements.editDeckForm.style.display = 'block';
    
    // Pré-remplir le formulaire avec les données actuelles
    elements.editDeckName.value = appState.selectedDeck.name || '';
    elements.editDeckDescription.value = appState.selectedDeck.description || '';
    elements.editDeckVisibility.value = appState.selectedDeck.is_public ? 'public' : 'private';
    
    // Initialize tags manager for edit form
    if (window.tagsManager && !window.tagsManager.isInitialized) {
        window.tagsManager.init('editDeckTagsInput', 'editDeckTagsDisplay');
    }
    if (window.tagsManager) {
        window.tagsManager.setTags(appState.selectedDeck.tags || []);
    }
    
    // Focus sur le nom
    elements.editDeckName.focus();
}

function hideEditDeckForm() {
    const elements = getElements();
    elements.editDeckForm.style.display = 'none';
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

async function saveEditDeck() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    const elements = getElements();
    const name = elements.editDeckName.value.trim();
    const description = elements.editDeckDescription.value.trim();
    const isPublic = elements.editDeckVisibility.value === 'public';
    
    if (!name) {
        window.notificationService.error('Le nom du deck est requis');
        elements.editDeckName.focus();
        return;
    }
    
    try {
        const deckData = {
            name: name,
            description: description,
            is_public: isPublic,
            tags: window.tagsManager ? window.tagsManager.getTags() : []
        };
        
        const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, deckData);
        
        window.notificationService.success('Deck modifié avec succès');
        
        // Mettre à jour l'état local
        appState.selectedDeck = updatedDeck;
        
        // Recharger la liste des decks et sélectionner le deck modifié
        await loadDecks();
        await selectDeck(updatedDeck.id);
        
        hideEditDeckForm();
        
    } catch (error) {
        console.error('Error updating deck:', error);
        window.notificationService.error('Erreur lors de la modification du deck');
    }
}

async function exportDeck() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    try {
        // Récupérer les cartes du deck
        const cardsResponse = await revisionAPI.getCards(appState.selectedDeck.id);
        const cards = cardsResponse.results || cardsResponse || [];
        
        if (cards.length === 0) {
            window.notificationService.warning('Ce deck ne contient aucune carte à exporter');
            return;
        }
        
        // Créer les données CSV
        const csvData = [
            ['Recto', 'Verso', 'Apprise', 'Date de création'],
            ...cards.map(card => [
                card.front_text,
                card.back_text,
                card.learned ? 'Oui' : 'Non',
                new Date(card.created_at).toLocaleDateString('fr-FR')
            ])
        ];
        
        // Convertir en CSV
        const csvContent = csvData.map(row => 
            row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(',')
        ).join('\n');
        
        // Créer le blob et télécharger
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `${appState.selectedDeck.name}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.notificationService.success(`Deck exporté : ${cards.length} cartes`);
        
    } catch (error) {
        console.error('Error exporting deck:', error);
        window.notificationService.error('Erreur lors de l\'exportation du deck');
    }
}

async function shareDeck() {
    console.log('shareDeck called, selectedDeck:', appState.selectedDeck);
    
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun jeu de cartes sélectionné');
        return;
    }
    
    // Wait for modal to be available (with timeout)
    const waitForModal = (modalId, maxWait = 5000) => {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const checkModal = () => {
                const modal = document.getElementById(modalId);
                if (modal) {
                    console.log(`Modal ${modalId} found after ${Date.now() - startTime}ms`);
                    resolve(modal);
                } else if (Date.now() - startTime < maxWait) {
                    setTimeout(checkModal, 100);
                } else {
                    console.error(`Modal ${modalId} not found after ${maxWait}ms`);
                    resolve(null);
                }
            };
            checkModal();
        });
    };
    
    if (!appState.selectedDeck.is_public) {
        // Deck is private, show make public modal
        console.log('Looking for makePublicModal...');
        let modalElement = document.getElementById('makePublicModal');
        
        if (!modalElement) {
            console.log('makePublicModal not found, creating it dynamically...');
            // Immediately create modals dynamically since we know they're not in template
            ensureModalsExist();
            
            // Give a brief moment for DOM to update
            await new Promise(resolve => setTimeout(resolve, 100));
            modalElement = document.getElementById('makePublicModal');
            
            if (!modalElement) {
                window.notificationService.error('Erreur: Impossible de créer le modal de partage');
                return;
            }
        }
        
        console.log('Opening makePublicModal:', modalElement);
        
        try {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            } else {
                // Fallback manuel
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                document.body.classList.add('modal-open');
                
                // Ajouter un backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                backdrop.onclick = () => {
                    modalElement.style.display = 'none';
                    modalElement.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    backdrop.remove();
                };
                document.body.appendChild(backdrop);
            }
        } catch (error) {
            console.error('Error with modal:', error);
            window.notificationService.error('Erreur lors de l\'ouverture de la modal');
        }
        return;
    }
    
    // Générer le lien de partage et afficher la modal de partage
    showShareModal();
}

async function showShareModal() {
    try {
        // Check if elements exist, if not create them immediately
        let shareModalElement = document.getElementById('shareModal');
        let shareUrlInput = document.getElementById('shareUrl');
        let shareModalDeckName = document.getElementById('shareModalDeckName');
        
        if (!shareModalElement || !shareUrlInput || !shareModalDeckName) {
            console.log('Share modal elements not found, creating them dynamically...');
            ensureModalsExist();
            
            // Give a brief moment for DOM to update
            await new Promise(resolve => setTimeout(resolve, 100));
            
            shareModalElement = document.getElementById('shareModal');
            shareUrlInput = document.getElementById('shareUrl');
            shareModalDeckName = document.getElementById('shareModalDeckName');
            
            if (!shareModalElement || !shareUrlInput || !shareModalDeckName) {
                window.notificationService.error('Erreur: Impossible de créer le modal de partage');
                return;
            }
        }
        
        // Générer le lien de partage et mettre à jour la modal
        const url = `${window.location.origin}/revision/explore/?deck=${appState.selectedDeck.id}`;
        shareUrlInput.value = url;
        shareModalDeckName.textContent = `"${appState.selectedDeck.name || 'Jeu de cartes sans nom'}"`;
        
        // Afficher la modal
        if (typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(shareModalElement);
            modal.show();
        } else if (typeof $ !== 'undefined' && $.fn.modal) {
            console.log('Using jQuery modal for share');
            $(shareModalElement).modal('show');
        } else {
            // Fallback ultime: afficher la modal manuellement
            console.log('Using manual modal display for share');
            shareModalElement.style.display = 'block';
            shareModalElement.classList.add('show');
            document.body.classList.add('modal-open');
            
            // Ajouter un backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.onclick = () => {
                shareModalElement.style.display = 'none';
                shareModalElement.classList.remove('show');
                document.body.classList.remove('modal-open');
                backdrop.remove();
            };
            document.body.appendChild(backdrop);
        }
    } catch (error) {
        console.error('Error with share modal:', error);
        window.notificationService.error('Erreur lors de l\'ouverture de la modal de partage');
    }
}

// Variable pour éviter la double initialisation
let shareModalHandlersSetup = false;

function setupShareModalEventHandlers() {
    if (shareModalHandlersSetup) {
        console.log('Share modal handlers already setup');
        return;
    }
    
    // Utiliser la délégation d'événements sur document pour éviter les problèmes de timing
    document.addEventListener('click', async function(e) {
        // Handler pour le bouton "Rendre public et partager"
        if (e.target.id === 'makeDeckPublicBtn' || e.target.closest('#makeDeckPublicBtn')) {
            e.preventDefault();
            const button = e.target.closest('#makeDeckPublicBtn') || e.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Mise à jour...';
            button.disabled = true;
            
            try {
                const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, {
                    is_public: true
                });
                
                appState.selectedDeck = updatedDeck;
                window.notificationService.success('Jeu de cartes rendu public avec succès !');
                
                // Fermer la modal actuelle et afficher la modal de partage
                const makePublicModal = bootstrap.Modal.getInstance(document.getElementById('makePublicModal'));
                if (makePublicModal) {
                    makePublicModal.hide();
                }
                showShareModal();
                
            } catch (error) {
                console.error('Error making deck public:', error);
                window.notificationService.error('Erreur lors de la publication du jeu de cartes');
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
        
        // Handler pour le bouton copier
        if (e.target.id === 'copyShareUrlBtn' || e.target.closest('#copyShareUrlBtn')) {
            e.preventDefault();
            const button = e.target.closest('#copyShareUrlBtn') || e.target;
            const input = document.getElementById('shareUrl');
            if (!input) return;
            
            input.select();
            input.setSelectionRange(0, 99999); // Pour mobile
            
            try {
                document.execCommand('copy');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check-circle me-1"></i>Copié !';
                button.style.backgroundColor = 'var(--linguify-accent, #017e84)';
                button.style.borderColor = 'var(--linguify-accent, #017e84)';
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.backgroundColor = 'var(--linguify-primary, #2D5BBA)';
                    button.style.borderColor = 'var(--linguify-primary, #2D5BBA)';
                }, 2000);
                
                window.notificationService.success('Lien copié dans le presse-papiers !');
            } catch (err) {
                window.notificationService.error('Impossible de copier le lien');
                console.error('Copy failed:', err);
            }
        }
        
        // Handlers pour les boutons de partage social
        if (e.target.classList.contains('social-share-btn') || e.target.closest('.social-share-btn')) {
            e.preventDefault();
            const button = e.target.closest('.social-share-btn') || e.target;
            const platform = button.dataset.platform;
            const shareUrlInput = document.getElementById('shareUrl');
            if (!shareUrlInput || !platform) return;
            
            const url = shareUrlInput.value;
            shareOnSocial(platform, url);
        }
    });
    
    shareModalHandlersSetup = true;
    console.log('Share modal event handlers configured with event delegation');
}

function shareOnSocial(platform, url) {
    const deckName = appState.selectedDeck.name || 'Jeu de cartes de révision';
    const text = `Découvrez mon jeu de cartes de révision "${deckName}" sur OpenLinguify !`;
    
    let shareUrl = '';
    
    switch (platform) {
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
            break;
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
            break;
        default:
            return;
    }
    
    window.open(shareUrl, '_blank', 'width=600,height=400,scrollbars=yes,resizable=yes');
}

function updateArchiveButton() {
    const archiveButton = document.getElementById('archiveDeck');
    if (!archiveButton || !appState.selectedDeck) return;
    
    const isArchived = appState.selectedDeck.is_archived;
    const icon = archiveButton.querySelector('i');
    const text = isArchived ? 'Désarchiver' : 'Archiver';
    const iconClass = isArchived ? 'bi-archive-fill' : 'bi-archive';
    
    // Update icon
    if (icon) {
        icon.className = `${iconClass} me-2`;
    }
    
    // Update text (keep the icon and just update the text part)
    archiveButton.innerHTML = `<i class="${iconClass} me-2"></i>${text}`;
}

function updateCardsCount() {
    const cardsCountElement = document.getElementById('cardsCount');
    if (!cardsCountElement || !appState.selectedDeck) return;
    
    const count = appState.selectedDeck.cards_count || 0;
    cardsCountElement.textContent = `${count} carte${count > 1 ? 's' : ''}`;
}

// === LANGUAGE SETTINGS FOR DECK ===

function showDeckLanguageSettings(deck) {
    const languageSettings = document.getElementById('deckLanguageSettings');
    if (!languageSettings) return;
    
    // Show language settings only if deck has cards
    if (deck.cards_count && deck.cards_count > 0) {
        languageSettings.style.display = 'block';
        
        // Initialize event listeners if not already done
        if (!languageSettings.hasAttribute('data-initialized')) {
            initializeDeckLanguageEvents();
            languageSettings.setAttribute('data-initialized', 'true');
        }
        
        // Populate language selectors with current deck settings
        const frontLangSelect = document.getElementById('deckFrontLanguage');
        const backLangSelect = document.getElementById('deckBackLanguage');
        
        console.log(`[Language Settings] DEBUG - Deck object:`, deck);
        console.log(`[Language Settings] DEBUG - Front language from API: "${deck.default_front_language}"`);
        console.log(`[Language Settings] DEBUG - Back language from API: "${deck.default_back_language}"`);
        
        // Temporarily disable auto-save during initialization
        window.isInitializingLanguageSettings = true;
        
        if (frontLangSelect) {
            const frontValue = deck.default_front_language || '';
            frontLangSelect.value = frontValue;
            console.log(`[Language Settings] Set front language selector to: "${frontValue}"`);
        } else {
            console.error('[Language Settings] Front language selector not found!');
        }
        
        if (backLangSelect) {
            const backValue = deck.default_back_language || '';
            backLangSelect.value = backValue;
            console.log(`[Language Settings] Set back language selector to: "${backValue}"`);
        } else {
            console.error('[Language Settings] Back language selector not found!');
        }
        
        // Re-enable auto-save after a short delay to ensure all initialization is complete
        setTimeout(() => {
            window.isInitializingLanguageSettings = false;
            console.log('[Language Settings] ✅ Auto-save re-enabled after initialization');
        }, 100);
    } else {
        languageSettings.style.display = 'none';
    }
}

function initializeDeckLanguageEvents() {
    const applyToDeckBtn = document.getElementById('applyLanguagesToDeck');
    const applyToNewCardsBtn = document.getElementById('applyLanguagesToNewCards');
    const frontLangSelect = document.getElementById('deckFrontLanguage');
    const backLangSelect = document.getElementById('deckBackLanguage');
    
    if (applyToDeckBtn) {
        applyToDeckBtn.addEventListener('click', applyLanguagesToAllCards);
    }
    
    if (applyToNewCardsBtn) {
        applyToNewCardsBtn.addEventListener('click', setDefaultLanguagesForNewCards);
    }
    
    // Auto-save language preferences when they change
    if (frontLangSelect) {
        frontLangSelect.addEventListener('change', saveDeckLanguagePreferences);
    }
    
    if (backLangSelect) {
        backLangSelect.addEventListener('change', saveDeckLanguagePreferences);
    }
}

async function applyLanguagesToAllCards() {
    if (!appState.selectedDeck) return;
    
    const frontLang = document.getElementById('deckFrontLanguage').value;
    const backLang = document.getElementById('deckBackLanguage').value;
    
    if (!frontLang && !backLang) {
        window.notificationService.error('Veuillez sélectionner au moins une langue');
        return;
    }
    
    const confirmMessage = `Voulez-vous appliquer ces langues à toutes les ${appState.selectedDeck.cards_count} cartes du deck ?\n\n` +
                          `Recto: ${frontLang ? getLanguageName(frontLang) : 'Détection automatique'}\n` +
                          `Verso: ${backLang ? getLanguageName(backLang) : 'Détection automatique'}`;
    
    if (!confirm(confirmMessage)) return;
    
    try {
        // Get all cards of the deck
        const deck = await revisionAPI.getDeck(appState.selectedDeck.id);
        
        for (const card of deck.cards || []) {
            const updateData = {};
            if (frontLang) updateData.front_language = frontLang;
            if (backLang) updateData.back_language = backLang;
            
            await revisionAPI.updateCard(card.id, updateData);
        }
        
        window.notificationService.success(`Langues appliquées à ${deck.cards_count || 0} cartes`);
        
        // Reload deck to refresh data
        await selectDeck(appState.selectedDeck.id);
        
    } catch (error) {
        console.error('Error applying languages to cards:', error);
        window.notificationService.error('Erreur lors de la mise à jour des langues');
    }
}

function setDefaultLanguagesForNewCards() {
    const frontLang = document.getElementById('deckFrontLanguage').value;
    const backLang = document.getElementById('deckBackLanguage').value;
    
    // Store in app state for future use
    if (!appState.deckDefaults) {
        appState.deckDefaults = {};
    }
    
    appState.deckDefaults.frontLanguage = frontLang;
    appState.deckDefaults.backLanguage = backLang;
    
    // Update the card creation forms with these defaults
    const newCardFrontLang = document.getElementById('newCardFrontLang');
    const newCardBackLang = document.getElementById('newCardBackLang');
    
    if (newCardFrontLang) newCardFrontLang.value = frontLang;
    if (newCardBackLang) newCardBackLang.value = backLang;
    
    const message = `Langues définies pour les nouvelles cartes :\n` +
                   `Recto: ${frontLang ? getLanguageName(frontLang) : 'Détection automatique'}\n` +
                   `Verso: ${backLang ? getLanguageName(backLang) : 'Détection automatique'}`;
    
    window.notificationService.success('Paramètres appliqués aux nouvelles cartes');
}

function getLanguageName(code) {
    const languages = {
        'fr': '🇫🇷 Français',
        'en': '🇺🇸 Anglais', 
        'es': '🇪🇸 Espagnol',
        'it': '🇮🇹 Italien',
        'de': '🇩🇪 Allemand',
        'pt': '🇵🇹 Portugais'
    };
    return languages[code] || code;
}

async function saveDeckLanguagePreferences() {
    console.log('[Language Settings] 🔄 saveDeckLanguagePreferences() called');
    
    // Skip auto-save during initialization to prevent overwriting user changes
    if (window.isInitializingLanguageSettings) {
        console.log('[Language Settings] ⏸️ Skipping auto-save during initialization');
        return;
    }
    
    if (!appState.selectedDeck) {
        console.warn('[Language Settings] No deck selected, cannot save language preferences');
        return;
    }
    
    const frontLangSelect = document.getElementById('deckFrontLanguage');
    const backLangSelect = document.getElementById('deckBackLanguage');
    
    if (!frontLangSelect || !backLangSelect) {
        console.error('[Language Settings] Language selectors not found');
        return;
    }
    
    const frontLang = frontLangSelect.value;
    const backLang = backLangSelect.value;
    
    console.log(`[Language Settings] 💾 Saving deck ${appState.selectedDeck.id} language preferences - Front: "${frontLang}" (empty=${!frontLang}), Back: "${backLang}" (empty=${!backLang})`);
    
    try {
        // Update the deck with new language preferences
        const updateData = {
            default_front_language: frontLang,
            default_back_language: backLang
        };
        
        console.log('[Language Settings] 📤 Sending API update with data:', updateData);
        
        const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, updateData);
        
        console.log('[Language Settings] 📥 API response received:', updatedDeck);
        
        // Update the local state
        appState.selectedDeck.default_front_language = frontLang;
        appState.selectedDeck.default_back_language = backLang;
        
        console.log('[Language Settings] ✅ Language preferences saved successfully');
        
        // Show a subtle notification
        if (window.notificationService) {
            window.notificationService.success('Préférences de langue sauvegardées');
        }
        
    } catch (error) {
        console.error('[Language Settings] ❌ Error saving language preferences:', error);
        
        if (window.notificationService) {
            window.notificationService.error('Erreur lors de la sauvegarde des préférences');
        }
        
        // Revert the selectors to their previous values
        frontLangSelect.value = appState.selectedDeck.default_front_language || '';
        backLangSelect.value = appState.selectedDeck.default_back_language || '';
    }
}

async function archiveDeck() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    const deckName = appState.selectedDeck.name;
    const isArchived = appState.selectedDeck.is_archived;
    
    showArchiveConfirmationModal(deckName, isArchived);
}

function showArchiveConfirmationModal(deckName, isArchived) {
    const action = isArchived ? 'désarchiver' : 'archiver';
    const actionTitle = isArchived ? 'Désarchiver le deck' : 'Archiver le deck';
    const actionDescription = isArchived ? 
        'Le deck redeviendra visible dans votre liste principale' : 
        'Le deck sera déplacé vers vos archives';
    const iconClass = isArchived ? 'bi-archive-fill' : 'bi-archive';
    
    // Utiliser les couleurs Linguify
    const bgColor = isArchived ? '#e8f5e8' : '#e8f0fe'; // Vert clair pour désarchiver, bleu clair pour archiver
    const borderColor = isArchived ? '#017e84' : '#2D5BBA'; // Accent vert pour désarchiver, primary bleu pour archiver
    const textColor = isArchived ? '#017e84' : '#2D5BBA';
    const btnBgColor = isArchived ? '#017e84' : '#2D5BBA'; // Accent pour désarchiver, primary pour archiver
    
    // Créer la modal de confirmation
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <div class="d-flex align-items-center">
                            <div class="rounded-circle p-2 me-3" style="background-color: ${bgColor};">
                                <i class="${iconClass}" style="font-size: 1.5rem; color: ${textColor};"></i>
                            </div>
                            <div>
                                <h5 class="modal-title mb-0" style="color: ${textColor};">${actionTitle}</h5>
                                <p class="text-muted mb-0 small">${actionDescription}</p>
                            </div>
                        </div>
                        <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                    </div>
                    <div class="modal-body pt-2">
                        <div class="alert border" style="background-color: ${bgColor}; border-color: ${borderColor} !important;">
                            <div class="d-flex align-items-start">
                                <i class="bi bi-info-circle-fill me-2 mt-1" style="color: ${textColor};"></i>
                                <div>
                                    <strong>Confirmer l'action</strong>
                                    <p class="mb-0 mt-1">
                                        Voulez-vous vraiment ${action} le deck <strong>"${deckName}"</strong> ?
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-outline-secondary" onclick="this.closest('.modal').remove()">
                            <i class="bi bi-x-lg me-1"></i>
                            Annuler
                        </button>
                        <button type="button" class="btn text-white" style="background-color: ${btnBgColor}; border-color: ${btnBgColor};" onclick="executeArchiveDeck(${!isArchived})">
                            <i class="${iconClass} me-1"></i>
                            ${actionTitle}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Fermer avec Escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

async function executeArchiveDeck(shouldArchive) {
    // Fermer la modal
    document.querySelector('.modal')?.remove();
    
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    try {
        const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, {
            is_archived: shouldArchive
        });
        
        appState.selectedDeck = updatedDeck;
        
        const message = updatedDeck.is_archived ? 'Deck archivé' : 'Deck désarchivé';
        window.notificationService.success(message);
        
        // Recharger la liste des decks
        await loadDecks();
        
        // Si le deck est archivé, revenir à la vue d'accueil
        if (updatedDeck.is_archived) {
            hideAllSections();
            const elements = getElements();
            elements.welcomeState.style.display = 'block';
            appState.selectedDeck = null;
        } else {
            await selectDeck(updatedDeck.id);
        }
        
    } catch (error) {
        console.error('Error archiving deck:', error);
        const action = shouldArchive ? 'archiv' : 'désarchiv';
        window.notificationService.error(`Erreur lors de l'${action}age du deck`);
    }
}

async function deleteDeckConfirm() {
    if (!appState.selectedDeck) {
        window.notificationService.error('Aucun deck sélectionné');
        return;
    }
    
    const deckName = appState.selectedDeck.name;
    const cardsCount = appState.selectedDeck.cards_count || 0;
    
    showDeleteConfirmationModal(deckName, cardsCount);
}

function showDeleteConfirmationModal(deckName, cardsCount) {
    // Créer la modal de confirmation
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <div class="d-flex align-items-center">
                            <div class="bg-danger bg-opacity-10 rounded-circle p-2 me-3">
                                <i class="bi bi-trash text-danger" style="font-size: 1.5rem;"></i>
                            </div>
                            <div>
                                <h5 class="modal-title text-danger mb-0">Supprimer le deck</h5>
                                <p class="text-muted mb-0 small">Cette action est irréversible</p>
                            </div>
                        </div>
                        <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                    </div>
                    <div class="modal-body pt-2">
                        <div class="alert alert-danger bg-danger bg-opacity-10 border-danger border-opacity-25">
                            <div class="d-flex align-items-start">
                                <i class="bi bi-exclamation-triangle-fill text-danger me-2 mt-1"></i>
                                <div>
                                    <strong>Attention !</strong> Vous êtes sur le point de supprimer définitivement :
                                    <ul class="mb-0 mt-2">
                                        <li>Le deck <strong>"${deckName}"</strong></li>
                                        ${cardsCount > 0 ? `<li>Ses <strong>${cardsCount} carte${cardsCount > 1 ? 's' : ''}</strong></li>` : ''}
                                        <li>Tout l'historique de révision associé</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <p class="text-muted mb-2">Pour confirmer la suppression, tapez le nom du deck :</p>
                            <input type="text" class="form-control" id="deleteConfirmInput" 
                                   placeholder="Tapez '${deckName}' pour confirmer" 
                                   autocomplete="off">
                        </div>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-outline-secondary" onclick="this.closest('.modal').remove()">
                            <i class="bi bi-x-lg me-1"></i>
                            Annuler
                        </button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn" disabled 
                                onclick="executeDeleteDeck('${deckName}')">
                            <i class="bi bi-trash me-1"></i>
                            Supprimer définitivement
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Gérer la validation du nom
    const input = modal.querySelector('#deleteConfirmInput');
    const confirmBtn = modal.querySelector('#confirmDeleteBtn');
    
    input.addEventListener('input', function() {
        const isValid = this.value.trim() === deckName;
        confirmBtn.disabled = !isValid;
        
        if (isValid) {
            confirmBtn.classList.remove('btn-danger');
            confirmBtn.classList.add('btn-outline-danger');
        } else {
            confirmBtn.classList.remove('btn-outline-danger');
            confirmBtn.classList.add('btn-danger');
        }
    });
    
    // Focus sur l'input
    setTimeout(() => input.focus(), 100);
    
    // Fermer avec Escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

async function executeDeleteDeck(deckName) {
    try {
        // Fermer la modal
        const modal = document.querySelector('.modal');
        if (modal) modal.remove();
        
        // Afficher un loading
        window.notificationService.info('Suppression en cours...');
        
        await revisionAPI.deleteDeck(appState.selectedDeck.id);
        
        window.notificationService.success(`Deck "${deckName}" supprimé avec succès`);
        
        // Revenir à la vue d'accueil
        hideAllSections();
        const elements = getElements();
        elements.welcomeState.style.display = 'block';
        appState.selectedDeck = null;
        
        // Recharger la liste des decks
        await loadDecks();
        
    } catch (error) {
        console.error('Error deleting deck:', error);
        window.notificationService.error('Erreur lors de la suppression du deck');
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

// Tags filter functions
function toggleTagsFilter() {
    const dropdown = document.getElementById('tagsFilterDropdown');
    const toggle = document.getElementById('tagsFilterToggle');
    
    // Check if dropdown is visible using computed style, not inline style
    const isVisible = dropdown.classList.contains('show') || 
                     (window.getComputedStyle(dropdown).display !== 'none' && dropdown.style.display !== 'none');
    
    if (!isVisible) {
        loadTagsFilter();
        
        // Position the dropdown using fixed positioning
        const rect = toggle.getBoundingClientRect();
        dropdown.style.top = (rect.bottom + 4) + 'px';  // 4px gap below button
        dropdown.style.left = (rect.right - 200) + 'px'; // Align right edge with dropdown width
        
        // S'assurer que le dropdown ne dépasse pas de l'écran
        const dropdownWidth = 200;
        if (rect.right - dropdownWidth < 0) {
            dropdown.style.left = '10px'; // Marge minimale du bord gauche
        }
        
        dropdown.classList.add('show');
        dropdown.style.display = 'block';
        toggle.classList.add('active');
    } else {
        dropdown.classList.remove('show');
        dropdown.style.display = 'none';
        toggle.classList.remove('active');
    }
}

function handleTagsFilterOutsideClick(event) {
    const dropdown = document.getElementById('tagsFilterDropdown');
    const toggle = document.getElementById('tagsFilterToggle');
    
    if (!dropdown.contains(event.target) && !toggle.contains(event.target)) {
        dropdown.classList.remove('show');
        dropdown.style.display = 'none';
        toggle.classList.remove('active');
    }
}

async function loadTagsFilter() {
    const dropdown = document.getElementById('tagsFilterDropdown');
    
    try {
        const response = await window.apiService.request('/api/v1/revision/tags/');
        const tags = response.tags || [];
        
        dropdown.innerHTML = `
            <div class="tags-filter-header">
                <span>Filtrer par tags</span>
                <button class="btn btn-link btn-sm p-0" onclick="clearTagsFilter()">
                    <i class="bi bi-x-circle"></i>
                </button>
            </div>
            <div class="tags-filter-list">
                ${tags.map(tag => `
                    <div class="tags-filter-item ${appState.filters.tags.includes(tag) ? 'active' : ''}" 
                         onclick="toggleTagFilter('${tag}')">
                        ${tag}
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Erreur lors du chargement des tags:', error);
        dropdown.innerHTML = '<div class="p-2 text-muted">Erreur lors du chargement des tags</div>';
    }
}

function toggleTagFilter(tag) {
    const index = appState.filters.tags.indexOf(tag);
    
    if (index === -1) {
        appState.filters.tags.push(tag);
    } else {
        appState.filters.tags.splice(index, 1);
    }
    
    updateTagsFilterCounter();
    loadDecks();
    loadTagsFilter(); // Refresh the filter display
}

function clearTagsFilter() {
    appState.filters.tags = [];
    updateTagsFilterCounter();
    loadDecks();
    loadTagsFilter(); // Refresh the filter display
}

function updateTagsFilterCounter() {
    const countElement = document.getElementById('tagsFilterCount');
    const toggleButton = document.getElementById('tagsFilterToggle');
    const count = appState.filters.tags.length;
    
    if (count > 0) {
        countElement.textContent = count;
        countElement.style.display = 'inline-block';
        toggleButton.classList.add('active');
    } else {
        countElement.style.display = 'none';
        toggleButton.classList.remove('active');
    }
}

// Quick tags editing (OpenLinguify style) - Open tags management directly
function quickEditTags(deckId) {
    console.log('🏷️ quickEditTags appelé avec deckId:', deckId);
    
    const deck = appState.decks.find(d => d.id === deckId);
    if (!deck) {
        console.error('❌ Deck non trouvé pour l\'ID:', deckId);
        return;
    }
    
    console.log('✅ Deck trouvé:', deck.name, 'Tags actuels:', deck.tags);
    
    // Store the deck ID for the tags management
    if (window.tagsManagement) {
        console.log('✅ tagsManagement trouvé, initialisation...');
        window.tagsManagement.setCurrentDeck(deckId);
        window.tagsManagement.showTagsManagement();
    } else {
        console.error('❌ window.tagsManagement non trouvé !');
    }
}

// Les fonctions de la modal rapide ne sont plus nécessaires
// car on utilise maintenant directement la modal de gestion des tags

function handleQuickTagKeypress(event, deckId) {
    if (event.key === 'Enter') {
        event.preventDefault();
        addQuickTag(deckId);
    }
}

async function addQuickTag(deckId) {
    const input = document.getElementById('quickTagInput');
    const tagValue = input.value.trim();
    
    if (!tagValue) return;
    
    try {
        const deck = appState.decks.find(d => d.id === deckId);
        const currentTags = deck.tags || [];
        
        if (currentTags.includes(tagValue)) {
            window.notificationService?.warning('Ce tag existe déjà');
            return;
        }
        
        const updatedTags = [...currentTags, tagValue];
        
        await revisionAPI.updateDeck(deckId, { tags: updatedTags });
        
        // Update local state
        deck.tags = updatedTags;
        
        // Refresh modal
        updateQuickTagsDisplay(deckId);
        input.value = '';
        
        // Refresh deck list
        renderDecksList();
        
        window.notificationService?.success('Tag ajouté');
    } catch (error) {
        console.error('Error adding tag:', error);
        window.notificationService?.error('Erreur lors de l\'ajout du tag');
    }
}

async function removeQuickTag(tag, deckId) {
    try {
        const deck = appState.decks.find(d => d.id === deckId);
        const updatedTags = (deck.tags || []).filter(t => t !== tag);
        
        await revisionAPI.updateDeck(deckId, { tags: updatedTags });
        
        // Update local state
        deck.tags = updatedTags;
        
        // Refresh modal
        updateQuickTagsDisplay(deckId);
        
        // Refresh deck list
        renderDecksList();
        
        window.notificationService?.success('Tag supprimé');
    } catch (error) {
        console.error('Error removing tag:', error);
        window.notificationService?.error('Erreur lors de la suppression du tag');
    }
}

function updateQuickTagsDisplay(deckId) {
    const deck = appState.decks.find(d => d.id === deckId);
    const container = document.getElementById('quickCurrentTags');
    if (container && deck) {
        container.innerHTML = (deck.tags || []).map(tag => `
            <span class="tag-pill" onclick="removeQuickTag('${tag}', ${deckId})">
                ${tag} <i class="bi bi-x"></i>
            </span>
        `).join('');
    }
}

async function loadQuickTagSuggestions() {
    try {
        const response = await window.apiService.request('/api/v1/revision/tags/');
        const tags = response.tags || [];
        
        const container = document.getElementById('quickSuggestedTags');
        if (container) {
            container.innerHTML = `
                <div class="suggestions-title">Tags populaires:</div>
                <div class="suggestions-list">
                    ${tags.slice(0, 6).map(tag => `
                        <span class="tag-suggestion" onclick="document.getElementById('quickTagInput').value='${tag}'">
                            ${tag}
                        </span>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading tag suggestions:', error);
    }
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
        
        // Deck details
        deckName: document.getElementById('deckName'),
        deckDescription: document.getElementById('deckDescription'),
        deckProgress: document.getElementById('deckProgress'),
        deckProgressBar: document.getElementById('deckProgressBar'),
        
        // Create form
        newDeckName: document.getElementById('newDeckName'),
        newDeckDescription: document.getElementById('newDeckDescription'),
        newDeckVisibility: document.getElementById('newDeckVisibility'),
        
        // Edit deck form
        editDeckForm: document.getElementById('editDeckForm'),
        editDeckName: document.getElementById('editDeckName'),
        editDeckDescription: document.getElementById('editDeckDescription'),
        editDeckVisibility: document.getElementById('editDeckVisibility'),
        saveEditDeck: document.getElementById('saveEditDeck'),
        cancelEditDeck: document.getElementById('cancelEditDeck'),
        cancelEditDeckAlt: document.getElementById('cancelEditDeckAlt'),
        
        // Import form
        importFile: document.getElementById('importFile'),
        importDeckName: document.getElementById('importDeckName'),
        
        // Import preview section
        importPreviewSection: document.getElementById('importPreviewSection'),
        previewFileName: document.getElementById('previewFileName'),
        previewTotalRows: document.getElementById('previewTotalRows'),
        frontColumnSelect: document.getElementById('frontColumnSelect'),
        backColumnSelect: document.getElementById('backColumnSelect'),
        previewCardsContainer: document.getElementById('previewCardsContainer'),
        confirmImport: document.getElementById('confirmImport'),
        cancelImportPreview: document.getElementById('cancelImportPreview'),
        cancelImportPreviewAlt: document.getElementById('cancelImportPreviewAlt'),
        
        // Create card form
        newCardFront: document.getElementById('newCardFront'),
        newCardBack: document.getElementById('newCardBack'),
        
        // Buttons
        createDeck: document.getElementById('createDeck'),
        importDeck: document.getElementById('importDeck'),
        refreshDecks: document.getElementById('refreshDecks'),
        backToList: document.getElementById('backToList'),
        addCard: document.getElementById('addCard'),
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
        cancelCardEditAlt: document.getElementById('cancelCardEditAlt'),
        
        // Study modes
        flashcardStudyMode: document.getElementById('flashcardStudyMode'),
        quizStudyMode: document.getElementById('quizStudyMode'),
        matchingStudyMode: document.getElementById('matchingStudyMode'),
        spacedStudyMode: document.getElementById('spacedStudyMode'),
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
    
    // Tags filter
    document.getElementById('tagsFilterToggle')?.addEventListener('click', toggleTagsFilter);
    document.addEventListener('click', handleTagsFilterOutsideClick);
    
    // Buttons
    elements.createDeck?.addEventListener('click', showCreateForm);
    elements.importDeck?.addEventListener('click', showImportForm);
    elements.refreshDecks?.addEventListener('click', loadDecks);
    elements.backToList?.addEventListener('click', backToList);
    elements.addCard?.addEventListener('click', showCreateCardForm);
    
    // Study mode buttons
    document.getElementById('studyFlashcards')?.addEventListener('click', startFlashcardsMode);
    document.getElementById('studyLearn')?.addEventListener('click', startLearnMode);
    document.getElementById('studyMatch')?.addEventListener('click', startMatchMode);
    document.getElementById('studyReview')?.addEventListener('click', startReviewMode);
    
    // Create form
    elements.submitCreate?.addEventListener('click', createNewDeck);
    elements.cancelCreate?.addEventListener('click', hideCreateForm);
    elements.cancelCreateAlt?.addEventListener('click', hideCreateForm);
    
    // Edit deck form
    elements.saveEditDeck?.addEventListener('click', saveEditDeck);
    elements.cancelEditDeck?.addEventListener('click', hideEditDeckForm);
    elements.cancelEditDeckAlt?.addEventListener('click', hideEditDeckForm);
    
    // Import form
    elements.submitImport?.addEventListener('click', importNewDeck);
    elements.cancelImport?.addEventListener('click', hideImportForm);
    elements.cancelImportAlt?.addEventListener('click', hideImportForm);
    
    // Import preview
    elements.confirmImport?.addEventListener('click', confirmImport);
    elements.cancelImportPreview?.addEventListener('click', cancelImportPreview);
    elements.cancelImportPreviewAlt?.addEventListener('click', cancelImportPreview);
    
    // Create card form
    elements.submitCardCreate?.addEventListener('click', createNewCard);
    elements.cancelCardCreate?.addEventListener('click', hideCreateCardForm);
    elements.cancelCardCreateAlt?.addEventListener('click', hideCreateCardForm);
    
    // Edit card form
    elements.submitCardEdit?.addEventListener('click', submitCardEdit);
    elements.cancelCardEdit?.addEventListener('click', hideEditCardForm);
    elements.cancelCardEditAlt?.addEventListener('click', hideEditCardForm);
    
    // Language modification buttons for new cards
    document.getElementById('changeFrontLang')?.addEventListener('click', toggleFrontLanguageSelector);
    document.getElementById('changeBackLang')?.addEventListener('click', toggleBackLanguageSelector);
    
    // Deck Management buttons
    document.getElementById('editDeck')?.addEventListener('click', showEditDeckForm);
    document.getElementById('exportDeck')?.addEventListener('click', exportDeck);
    const shareButton = document.getElementById('shareDeck');
    if (shareButton) {
        shareButton.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Share button clicked');
            shareDeck();
        });
        console.log('Share button event listener attached');
    } else {
        console.log('Share button not found in DOM');
    }
    document.getElementById('archiveDeck')?.addEventListener('click', archiveDeck);
    document.getElementById('deleteDeck')?.addEventListener('click', deleteDeckConfirm);
    
    // Create deck buttons
    document.querySelectorAll('.create-deck-btn').forEach(btn => {
        btn.addEventListener('click', showCreateForm);
    });
    
    // Load more
    elements.loadMoreBtn?.addEventListener('click', loadMoreDecks);
}

// Create modals dynamically if they don't exist in DOM
function ensureModalsExist() {
    // Check if modals already exist
    const makePublicModal = document.getElementById('makePublicModal');
    const shareModal = document.getElementById('shareModal');
    
    console.log('Checking modals existence:', {
        makePublicModal: !!makePublicModal,
        shareModal: !!shareModal
    });
    
    if (makePublicModal && shareModal) {
        console.log('Modals already exist in DOM');
        return;
    }
    
    console.log('Creating modals dynamically...');
    
    // Create makePublicModal
    const makePublicModalHTML = `
        <div class="modal fade" id="makePublicModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <div class="d-flex align-items-center">
                            <div class="rounded-circle p-2 me-3 share-modal-icon-bg">
                                <i class="bi bi-share share-modal-icon"></i>
                            </div>
                            <div>
                                <h5 class="modal-title mb-0 share-modal-title">Partager votre jeu de cartes</h5>
                                <p class="text-muted mb-0 small">Rendez votre jeu de cartes visible à tous</p>
                            </div>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body pt-2">
                        <div class="alert border-0" style="background-color: rgba(45, 91, 186, 0.08); border-left: 4px solid #2D5BBA !important;">
                            <div class="d-flex align-items-start">
                                <i class="bi bi-info-circle-fill me-2 mt-1" style="color: #2D5BBA;"></i>
                                <div>
                                    <strong style="color: #2D5BBA;">Jeu de cartes privé</strong><br>
                                    <span style="color: #6B7280;">Ce jeu de cartes est actuellement privé. Pour le partager, vous devez le rendre public.</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="fw-semibold mb-2" style="color: #6B7280;">
                                <i class="bi bi-eye me-1" style="color: #017e84;"></i>
                                En rendant ce jeu de cartes public :
                            </h6>
                            <ul class="list-unstyled ms-3">
                                <li class="mb-1" style="color: #6B7280;">
                                    <i class="bi bi-check-circle me-2" style="color: #017e84;"></i>
                                    Autres utilisateurs pourront le découvrir
                                </li>
                                <li class="mb-1" style="color: #6B7280;">
                                    <i class="bi bi-check-circle me-2" style="color: #017e84;"></i>
                                    Vous pourrez partager le lien
                                </li>
                                <li class="mb-1" style="color: #6B7280;">
                                    <i class="bi bi-check-circle me-2" style="color: #017e84;"></i>
                                    Vous restez propriétaire et pouvez le modifier
                                </li>
                            </ul>
                        </div>
                        
                        <div class="small" style="color: #6B7280;">
                            <i class="bi bi-shield-check me-1" style="color: #017e84;"></i>
                            Vous pourrez toujours rendre le jeu de cartes privé plus tard si nécessaire.
                        </div>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal" style="border-color: #6B7280; color: #6B7280;">
                            <i class="bi bi-x-circle me-1"></i>Annuler
                        </button>
                        <button type="button" class="btn" id="makeDeckPublicBtn" style="background-color: #2D5BBA; border-color: #2D5BBA; color: white;">
                            <i class="bi bi-share me-1"></i>Rendre public et partager
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Create shareModal
    const shareModalHTML = `
        <div class="modal fade" id="shareModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <div class="d-flex align-items-center">
                            <div class="rounded-circle p-2 me-3" style="background-color: rgba(0, 212, 170, 0.1);">
                                <i class="bi bi-share" style="font-size: 1.5rem; color: #017e84;"></i>
                            </div>
                            <div>
                                <h5 class="modal-title mb-0" style="color: #017e84;">Partager votre jeu de cartes</h5>
                                <p class="text-muted mb-0 small" id="shareModalDeckName">"Nom du jeu de cartes"</p>
                            </div>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body pt-2">
                        <p class="mb-3" style="color: #6B7280;">Partagez ce lien avec vos amis ou sur les réseaux sociaux :</p>
                        
                        <div class="mb-3">
                            <label class="form-label fw-semibold" style="color: #6B7280;">
                                <i class="bi bi-link-45deg me-1" style="color: #2D5BBA;"></i>Lien de partage
                            </label>
                            <div class="input-group">
                                <input type="text" class="form-control" readonly id="shareUrl" style="background-color: #f8f9fa; border-color: #2D5BBA;">
                                <button class="btn" id="copyShareUrlBtn" type="button" style="background-color: #2D5BBA; border-color: #2D5BBA; color: white;">
                                    <i class="bi bi-clipboard me-1"></i>Copier
                                </button>
                            </div>
                        </div>
                        
                        <div class="d-flex gap-2 flex-wrap">
                            <button class="btn btn-sm social-share-btn" data-platform="twitter" type="button" style="border: 1px solid #8B5CF6; color: #8B5CF6; background-color: rgba(139, 92, 246, 0.05);">
                                <i class="bi bi-twitter me-1"></i>Twitter
                            </button>
                            <button class="btn btn-sm social-share-btn" data-platform="facebook" type="button" style="border: 1px solid #8B5CF6; color: #8B5CF6; background-color: rgba(139, 92, 246, 0.05);">
                                <i class="bi bi-facebook me-1"></i>Facebook
                            </button>
                            <button class="btn btn-sm social-share-btn" data-platform="linkedin" type="button" style="border: 1px solid #8B5CF6; color: #8B5CF6; background-color: rgba(139, 92, 246, 0.05);">
                                <i class="bi bi-linkedin me-1"></i>LinkedIn
                            </button>
                        </div>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal" style="border-color: #6B7280; color: #6B7280;">
                            <i class="bi bi-x-circle me-1"></i>Fermer
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modals to DOM
    document.body.insertAdjacentHTML('beforeend', makePublicModalHTML);
    document.body.insertAdjacentHTML('beforeend', shareModalHTML);
    
    console.log('Modals created successfully');
}

// Debug function to check DOM state
function debugModalState() {
    console.log('=== DEBUG MODAL STATE ===');
    console.log('Template debug marker:', document.getElementById('template-debug-marker'));
    console.log('Share component debug marker:', document.getElementById('share-component-debug-marker'));
    console.log('makePublicModal:', document.getElementById('makePublicModal'));
    console.log('shareModal:', document.getElementById('shareModal'));
    console.log('shareUrl:', document.getElementById('shareUrl'));
    console.log('makeDeckPublicBtn:', document.getElementById('makeDeckPublicBtn'));
    console.log('copyShareUrlBtn:', document.getElementById('copyShareUrlBtn'));
    console.log('All modals in DOM:', document.querySelectorAll('.modal'));
    console.log('All divs with "modal" class:', document.querySelectorAll('div[class*="modal"]'));
    console.log('Body contains "makePublicModal":', document.body.innerHTML.includes('makePublicModal'));
    console.log('Body contains "share_deck.html":', document.body.innerHTML.includes('share_deck.html'));
    console.log('Full body HTML length:', document.body.innerHTML.length);
    console.log('Bootstrap available:', typeof bootstrap !== 'undefined');
    console.log('jQuery available:', typeof $ !== 'undefined');
    console.log('========================');
}

// Initialize the app
function initializeApp() {
    console.log('Initializing app...');
    setupEventListeners();
    
    // Setup share modal event handlers
    setupShareModalEventHandlers();
    
    loadDecks();
    
    // Debug après un délai pour laisser le DOM se charger complètement
    setTimeout(() => {
        console.log('=== DELAYED DEBUG MODAL STATE ===');
        debugModalState();
    }, 2000);
}

// Export for global access
window.revisionAPI = revisionAPI;
window.appState = appState;
window.renderDecksList = renderDecksList;
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
    toggleFrontLanguageSelector,
    toggleBackLanguageSelector,
    updateLanguageDisplay,
    resetLanguageSelectors,
    hideAllSections,
    createNewDeck,
    createNewCard,
    importNewDeck,
    updateCardsCount,
    loadDeckCards,
    backToDeckView,
    editCard,
    deleteCard,
    startFlashcardsMode,
    startLearnMode,
    startMatchMode,
    startReviewMode,
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
    getElements,
    
    
    // Import Preview
    showImportPreview,
    updatePreviewDisplay,
    updatePreview,
    confirmImport,
    cancelImportPreview,
    hideImportPreview,
    
    // Advanced Interactivity
    initializeDragAndDrop,
    handleFileSelect,
    validateFile,
    showSelectedFileInfo,
    clearSelectedFile,
    formatFileSize,
    initializeRealTimeValidation,
    validateDeckName,
    updateImportButton,
    animateValue,
    animateNumber,
    animateText,
    
    // Deck Management
    showEditDeckForm,
    hideEditDeckForm,
    saveEditDeck,
    exportDeck,
    shareDeck,
    archiveDeck,
    showArchiveConfirmationModal,
    executeArchiveDeck,
    deleteDeckConfirm,
    showDeleteConfirmationModal,
    executeDeleteDeck,
    
    // Share functions
    showShareModal,
    setupShareModalEventHandlers,
    shareOnSocial
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);