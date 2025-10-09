// Revision Main Interface Manager

// Translation helper function
function _(key, fallback = null) {
    return (window.translations && window.translations[key]) || fallback || key;
}

// Global application state
let appState = {
    decks: [],
    selectedDeck: null,
    isLoading: false,
    isRefreshing: false, // New state for refresh operations
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

// Optimized API Service
const revisionAPI = {
    async getDecks(page = 1, filters = {}) {
        const params = new URLSearchParams({
            page: page,
            ...filters
        });
        
        const url = `/api/v1/revision/api/decks/?${params}`;
        console.log('🌐 API request URL:', url);
        console.log('🌐 Filters being sent:', filters);
        
        return await window.apiService.request(url);
    },
    
    async getDeck(id) {
        console.log(`🔍 Requesting deck with ID: ${id}`);
        const url = `/api/v1/revision/api/decks/${id}/`;
        console.log(`🔍 Full URL: ${url}`);
        try {
            const result = await window.apiService.request(url);
            console.log(`✅ Deck loaded successfully:`, result);
            return result;
        } catch (error) {
            console.error(`❌ Failed to load deck ${id}:`, error);
            throw error;
        }
    },
    
    async createDeck(data) {
        return await window.apiService.request('/api/v1/revision/api/decks/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateDeck(id, data) {
        return await window.apiService.request(`/api/v1/revision/api/decks/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },
    
    async deleteDeck(id) {
        return await window.apiService.request(`/api/v1/revision/api/decks/${id}/`, {
            method: 'DELETE'
        });
    },
    
    async getStats() {
        return await window.apiService.request('/api/v1/revision/api/decks/stats/');
    },
    
    async previewImport(deckId, formData) {
        // Pour FormData, on doit gérer les headers différemment
        const csrfToken = window.apiService.getCSRFToken();
        return await fetch(`/api/v1/revision/api/decks/${deckId}/import/`, {
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
        return await fetch(`/api/v1/revision/api/decks/${deckId}/import/`, {
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
        return await window.apiService.request('/api/v1/revision/api/flashcards/', {
            method: 'POST',
            body: JSON.stringify({
                deck: deckId,
                ...cardData
            })
        });
    },
    
    async getCards(deckId, options = {}) {
        // Add timestamp to prevent caching issues
        const timestamp = Date.now();
        
        // Build query parameters
        const params = new URLSearchParams({
            _t: timestamp
        });
        
        // Add study mode if specified
        if (options.studyMode === 'smart') {
            params.append('study_mode', 'smart');
            
            // Add other spaced repetition parameters
            if (options.maxCards) params.append('max_cards', options.maxCards);
            if (options.newCards) params.append('new_cards', options.newCards);
            if (options.aheadDays) params.append('ahead_days', options.aheadDays);
            if (options.prioritizeOverdue !== undefined) params.append('prioritize_overdue', options.prioritizeOverdue);
            if (options.mixedOrder !== undefined) params.append('mixed_order', options.mixedOrder);
            
            // Use the deck cards endpoint for smart mode
            return await window.apiService.request(`/api/v1/revision/api/decks/${deckId}/cards/?${params}`);
        } else {
            // Normal mode - use flashcards endpoint
            params.append('deck', deckId);
            return await window.apiService.request(`/api/v1/revision/api/flashcards/?${params}`);
        }
    },
    
    async updateCard(cardId, cardData) {
        return await window.apiService.request(`/api/v1/revision/api/flashcards/${cardId}/`, {
            method: 'PATCH',
            body: JSON.stringify(cardData)
        });
    },
    
    async deleteCard(cardId) {
        return await window.apiService.request(`/api/v1/revision/api/flashcards/${cardId}/`, {
            method: 'DELETE'
        });
    },
    
    async getLearningSettings(deckId) {
        return await window.apiService.request(`/api/v1/revision/api/decks/${deckId}/learning_settings/`);
    },
    
    async updateLearningSettings(deckId, settings) {
        return await window.apiService.request(`/api/v1/revision/api/decks/${deckId}/learning_settings/`, {
            method: 'PATCH',
            body: JSON.stringify(settings)
        });
    },
    
    async applyPreset(deckId, presetName) {
        return await window.apiService.request(`/api/v1/revision/api/decks/${deckId}/apply_preset/`, {
            method: 'POST',
            body: JSON.stringify({ preset_name: presetName })
        });
    },
    
    async updateCardProgress(cardId, isCorrect, studyMode = 'flashcards', difficulty = null) {
        // Use new adaptive learning endpoint
        console.log('[AdaptiveLearning] updateCardProgress called:', {
            cardId,
            isCorrect,
            studyMode,
            difficulty: difficulty || (isCorrect ? 'easy' : 'hard')
        });

        return await window.apiService.request(`/revision/api/adaptive/card/${cardId}/review/`, {
            method: 'POST',
            body: JSON.stringify({
                study_mode: studyMode,
                difficulty: difficulty || (isCorrect ? 'easy' : 'hard'),
                was_correct: isCorrect,
                response_time_seconds: null
            })
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

// Update the share/privacy buttons based on the selected deck's visibility
function updateShareButtonText() {
    const shareButton = document.getElementById('shareDeck');
    const makePrivateButton = document.getElementById('makePrivateDeck');
    if (!shareButton || !appState.selectedDeck) return;
    
    const shareIcon = shareButton.querySelector('i');
    const shareTextNode = shareButton.childNodes[shareButton.childNodes.length - 1];
    
    if (appState.selectedDeck.is_public) {
        // Deck is already public - show share option and make private option
        if (shareIcon) {
            shareIcon.className = 'bi bi-share me-2';
        }
        if (shareTextNode) {
            shareTextNode.textContent = _('Share');
        }
        
        // Show "Rendre privé" option
        if (makePrivateButton) {
            makePrivateButton.style.display = 'block';
        }
    } else {
        // Deck is private - show make public option and hide make private option
        if (shareIcon) {
            shareIcon.className = 'bi bi-globe2 me-2';
        }
        if (shareTextNode) {
            shareTextNode.textContent = _('Make public');
        }
        
        // Hide "Rendre privé" option
        if (makePrivateButton) {
            makePrivateButton.style.display = 'none';
        }
    }
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
        
        // Use enhanced error handling with retry
        window.notificationService.handleApiError(
            error, 
            _('Loading decks'),
            () => loadDecks(reset) // Retry with same parameters
        );
    } finally {
        appState.isLoading = false;
    }
}

// Refresh function removed - now handled by HTMX

// Helper function to refresh the currently selected deck
async function refreshSelectedDeck() {
    if (!appState.selectedDeck) return;
    
    try {
        console.log(`🔄 Actualisation du deck sélectionné: ${appState.selectedDeck.name}`);
        const freshDeck = await revisionAPI.getDeck(appState.selectedDeck.id);
        appState.selectedDeck = freshDeck;
        
        // Refresh the deck view if we're currently viewing it
        const deckDetails = document.getElementById('deckDetails');
        if (deckDetails && deckDetails.style.display !== 'none') {
            // Update deck details display
            updateDeckDetailsDisplay(freshDeck);
            // Reload cards if cards are currently displayed
            await loadDeckCards();
        }
        
        console.log('✅ Deck sélectionné actualisé');
    } catch (error) {
        console.error('❌ ' + _('Error') + ' lors de l\'actualisation du deck sélectionné:', error);
        // Don't show error for this, as the main refresh might still succeed
    }
}

// Helper function to update deck details display
function updateDeckDetailsDisplay(deck) {
    const elements = getElements();
    if (!elements.deckDetails || elements.deckDetails.style.display === 'none') return;
    
    // Update basic deck info
    if (elements.deckName) elements.deckName.textContent = deck.name || _('Unnamed');
    if (elements.deckDescription) elements.deckDescription.textContent = deck.description || _('No description');
    
    // Update progress
    const progress = calculateProgress(deck);
    if (elements.deckProgress) elements.deckProgress.textContent = `${deck.learned_count || 0}/${deck.cards_count || 0}`;
    if (elements.deckProgressBar) elements.deckProgressBar.style.width = `${progress}%`;
    
    // Update cards count
    updateCardsCount();
    
    console.log('✅ Affichage du deck mis à jour');
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
        <li class="deck-card ${appState.selectedDeck?.id === deck.id ? 'active' : ''}" 
            onclick="selectDeck(${deck.id})">
            <div class="deck-card-header">
                <span class="deck-card-count">${deck.cards_count || 0}</span>
                <div class="deck-card-icons">
                    ${deck.is_public ? '<i class="bi bi-globe2 text-linguify-accent" title="Public"></i>' : ''}
                    ${deck.is_archived ? `<i class="bi bi-archive text-gray-400" title="${_('Archived')}"></i>` : ''}
                </div>
                <h4 class="deck-card-title">${deck.name || _('Unnamed')}</h4>
            </div>
            <div class="deck-card-description">${deck.description || _('No description')}</div>
            <div class="deck-card-tags">
                <div class="deck-tags">${window.displayDeckTags ? window.displayDeckTags(deck) : ((!deck.tags || deck.tags.length === 0) ? `<span class="no-tags-message" onclick="event.stopPropagation(); quickEditTags(${deck.id})" style="cursor: pointer;">${_('No tags - Click on 🏷️ to add some')}</span>` : deck.tags.map(tag => `<span class="tag-linguify tag-linguify-blue">${tag}</span>`).join(''))}</div>
                <button class="btn-link-linguify text-sm" onclick="event.stopPropagation(); quickEditTags(${deck.id})" title="${_('Add tags')}">
                    <i class="bi bi-tag"></i>
                </button>
            </div>
            <div class="deck-progress">
                <div class="progress-text">${deck.learned_count || 0}/${deck.cards_count || 0}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">${progress}%</div>
            </div>
            <div class="deck-date">${formatDate(deck.updated_at)}</div>
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

// Function to manage contextual navbar actions
function updateNavbarActions(showGeneralActions = true) {
    const generalActions = document.getElementById('generalActions');
    
    if (generalActions) {
        if (showGeneralActions) {
            generalActions.style.display = 'flex';
        } else {
            generalActions.style.display = 'none';
        }
    }
}

// UI Management Functions
async function selectDeck(deckId) {
    try {
        // Check authentication first
        const authCheck = await window.apiService.request('/api/v1/revision/debug/auth/');
        console.log('🔐 Auth check:', authCheck);
        
        if (!authCheck.authenticated) {
            console.error('❌ User not authenticated');
            window.notificationService.error(
                'Vous devez être connecté pour accéder à vos decks. ' +
                '<a href="/login/" style="color: white; text-decoration: underline;">Se connecter</a>'
            );
            return;
        }
        
        console.log(`✅ User authenticated as: ${authCheck.user} (ID: ${authCheck.user_id})`);
        
        const deck = await revisionAPI.getDeck(deckId);
        appState.selectedDeck = deck;
        
        // Update share button text based on deck visibility
        updateShareButtonText();
        
        // Hide all sections first
        hideAllSections();
        
        // Show deck details
        const elements = getElements();
        elements.deckDetails.style.display = 'block';
        
        // Populate deck details
        elements.deckName.textContent = deck.name || _('Unnamed');
        elements.deckDescription.textContent = deck.description || _('No description');
        
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
        
        // Keep general actions visible when deck is selected
        updateNavbarActions(true);
        
    } catch (error) {
        console.error('Error loading deck:', error);
        
        if (error.status === 404) {
            window.notificationService.error(
                `Deck non trouvé ou accès refusé (ID: ${deckId}). Vérifiez que vous êtes connecté et que vous avez accès à ce deck.`
            );
        } else if (error.status === 403) {
            window.notificationService.error(
                `Accès refusé à ce deck. Vérifiez vos permissions.`
            );
        } else if (error.status === 401) {
            window.notificationService.error(
                'Session expirée. Veuillez vous reconnecter. ' +
                '<a href="/login/" style="color: white; text-decoration: underline;">Se connecter</a>'
            );
        } else {
            window.notificationService.error(`${_('Error loading deck')}: ${error.message}`);
        }
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
        // Keep general actions visible when deck is selected
        updateNavbarActions(true);
    } else {
        elements.welcomeState.style.display = 'block';
        // Show general actions in welcome state
        updateNavbarActions(true);
    }
}

function showImportForm() {
    hideAllSections();
    
    const elements = getElements();
    elements.importDeckForm.style.display = 'block';
    
    // Clear form
    elements.importFile.value = '';
    elements.importDeckName.value = '';
    
    // Reset validation state - FORCE BRUTAL
    elements.importDeckName.classList.remove('is-valid', 'is-invalid');
    elements.importDeckName.removeAttribute('data-user-interacted');
    elements.importDeckName.style.borderColor = '#dee2e6'; // Force bordure grise
    elements.importDeckName.style.boxShadow = 'none'; // Supprime l'ombre
    const errorElement = document.getElementById('deckNameError');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
    
    // Double vérification après un délai
    setTimeout(() => {
        elements.importDeckName.classList.remove('is-valid', 'is-invalid');
        elements.importDeckName.style.borderColor = '#dee2e6';
        console.log('Force reset classes:', elements.importDeckName.className);
    }, 100);
    
    // Reset form state
    clearSelectedFile();
    updateImportButton();
    
    // Initialize drag and drop
    initializeDragAndDrop();

    // Initialize real-time validation
    initializeRealTimeValidation();

    // Initialize document import module
    if (typeof window.initDocumentImport === 'function') {
        window.initDocumentImport();
    }
}

function hideImportForm() {
    const elements = getElements();
    elements.importDeckForm.style.display = 'none';
    
    // Remettre les éléments du formulaire à leur état normal
    if (elements.importDeckName) {
        elements.importDeckName.readOnly = false;
        elements.importDeckName.style.backgroundColor = '';
        const formTitle = elements.importDeckForm.querySelector('h5');
        if (formTitle) {
            formTitle.textContent = 'Importer une liste de cartes';
        }
        if (elements.submitImport) {
            elements.submitImport.textContent = 'Prévisualiser';
        }
    }
    
    // Réinitialiser les flags d'import dans deck existant
    window.importToExistingDeck = false;
    window.targetDeckId = null;
    
    if (appState.selectedDeck) {
        elements.deckDetails.style.display = 'block';
    } else {
        elements.welcomeState.style.display = 'block';
    }
}

function showCreateCardForm() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('Please select a deck first'));
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
            button.innerHTML = `<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">${_('Edit')}</span>`;
            button.title = _('Edit language for this card');
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
            button.innerHTML = `<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">${_('Edit')}</span>`;
            button.title = _('Edit language for this card');
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
            display.textContent = _('Default deck language');
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
        frontButton.innerHTML = `<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">${_('Edit')}</span>`;
        frontButton.title = _('Edit language for this card');
    }
    if (frontDisplay) frontDisplay.textContent = _('Default deck language');
    
    // Reset back language selector
    const backSelector = document.getElementById('backLangSelector');
    const backButton = document.getElementById('changeBackLang');
    const backDisplay = document.getElementById('deckBackLangDisplay');
    
    if (backSelector) backSelector.style.display = 'none';
    if (backButton) {
        backButton.innerHTML = `<i class="bi bi-pencil" style="font-size: 0.75rem;"></i><span class="ms-1" style="font-size: 0.75rem;">${_('Edit')}</span>`;
        backButton.title = _('Edit language for this card');
    }
    if (backDisplay) backDisplay.textContent = _('Default deck language');
}

async function createNewCard() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    const elements = getElements();
    const frontText = elements.newCardFront.value.trim();
    const backText = elements.newCardBack.value.trim();
    const frontLang = document.getElementById('newCardFrontLang').value;
    const backLang = document.getElementById('newCardBackLang').value;
    
    if (!frontText) {
        window.notificationService.error(_('Front text is required'));
        elements.newCardFront.focus();
        return;
    }

    if (!backText) {
        window.notificationService.error(_('Back text is required'));
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

        window.notificationService.success(_('Card created successfully'));
        
        // Close form first
        hideCreateCardForm();
        
        // Reload everything to get fresh data
        await Promise.all([
            loadDecks(), // Reload deck list with updated counts
            selectDeck(appState.selectedDeck.id) // Reload selected deck details
        ]);
        
    } catch (error) {
        console.error('Error creating card:', error);
        window.notificationService.error(_('Error creating card'));
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
        
        // Handle different response formats:
        // 1. Paginated response: {results: [...]}
        // 2. Smart mode response: {cards: [...], study_session: {...}}
        // 3. Direct array response: [...]
        let cards = [];
        if (response.results) {
            cards = response.results; // Paginated response
        } else if (response.cards) {
            cards = response.cards; // Smart mode response
        } else if (Array.isArray(response)) {
            cards = response; // Direct array
        } else {
            console.error('Unexpected response format:', response);
            cards = [];
        }
        
        console.log('Raw cards data:', cards);
        console.log('First card sample:', cards[0]);
        
        // Filter cards to only show those belonging to the current deck
        const filteredCards = cards.filter(card => card.deck === deckId);
        console.log('Filtered cards:', filteredCards);
        console.log('First filtered card sample:', filteredCards[0]);
        
        console.log(`Found ${filteredCards.length} cards for deck ${deckId}`);
        
        if (!filteredCards || filteredCards.length === 0) {
            elements.cardsContainer.style.display = 'none';
            elements.noCardsMessage.style.display = 'block';
            return;
        }
        
        elements.noCardsMessage.style.display = 'none';
        elements.cardsContainer.style.display = 'block';
        
        // Render cards with deck ID for debugging
        elements.cardsContainer.innerHTML = filteredCards.map((card, index) => {
            const cardId = card.id || card.pk || `temp-${deckId}-${index}`;
            console.log('Rendering card with ID:', cardId, 'Card object:', card);
            
            return `
            <div class="card mb-3 position-relative" data-card-id="${cardId}">
                <div class="position-absolute" style="top: 8px; right: 8px; z-index: 10;">
                    <div class="d-flex gap-2">
                        <button class="btn btn-link p-0" 
                                onclick="window.revisionMain?.editCard(${cardId})" 
                                title="${_('Edit')}"
                                style="color: #6c757d; font-size: 0.9rem; border: none; background: none; text-decoration: none;">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-link p-0" 
                                onclick="window.revisionMain?.deleteCard(${cardId})" 
                                title="${_('Delete')}"
                                style="color: #6c757d; font-size: 0.9rem; border: none; background: none; text-decoration: none;">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-5">
                            <p class="card-text card-front-text mb-0">${card.front_text || ''}</p>
                        </div>
                        <div class="col-md-2 text-center">
                            <button class="btn btn-link p-0 card-flip-btn"
                                    onclick="window.flipCardTranslation(${cardId}, event)"
                                    title="${_('Flip card')}"
                                    style="color: #6c757d; font-size: 1rem; border: none; background: none; text-decoration: none; cursor: pointer;">
                                <i class="bi bi-arrow-left-right"></i>
                            </button>
                        </div>
                        <div class="col-md-5">
                            <p class="card-text card-back-text mb-0">${card.back_text || ''}</p>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div>
                            <span class="badge ${card.learned ? 'bg-linguify-accent' : 'bg-secondary'}">
                                ${card.learned ? _('Learned') : _('To learn')}
                            </span>
                            <small class="text-muted ms-2">
                                ${_('Created on')} ${formatDate(card.created_at)}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading deck cards:', error);
        window.notificationService.error(_('Error loading cards'));
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
    console.log('🔄 Starting flashcards mode...');
    console.log('📦 Selected deck:', appState.selectedDeck);
    console.log('🔧 window.flashcardMode exists:', !!window.flashcardMode);
    
    if (!appState.selectedDeck) {
        window.notificationService.error(_('Please select a deck first'));
        return;
    }
    
    if (window.flashcardMode) {
        console.log('✅ Starting flashcard study...');
        window.flashcardMode.startStudy(appState.selectedDeck);
    } else {
        console.error('❌ window.flashcardMode is not available');
        window.notificationService.error(_('Flashcards mode not available'));
    }
}

function startLearnMode() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('Please select a deck first'));
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
        window.notificationService.error(_('Please select a deck first'));
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
        window.notificationService.error(_('Please select a deck first'));
        return;
    }
    
    if (window.spacedMode) {
        window.spacedMode.startSpacedReview(appState.selectedDeck);
    } else {
        window.notificationService.error('Mode Révision rapide non disponible');
    }
}

function startWriteMode() {
    console.log('🖊️ startWriteMode called');
    console.log('selectedDeck:', appState.selectedDeck);
    console.log('window.writeMode:', window.writeMode);
    
    if (!appState.selectedDeck) {
        window.notificationService.error(_('Please select a deck first'));
        return;
    }
    
    if (window.writeMode) {
        console.log('✅ Starting write study mode');
        window.writeMode.startWriteStudy(appState.selectedDeck);
    } else {
        console.error('❌ window.writeMode not available');
        window.notificationService.error('Mode Écriture non disponible - module non chargé');
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
            window.notificationService.error(_('Card not found - it may have been deleted'));
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
            window.notificationService.error(_('This card no longer exists'));
            await loadDeckCards(); // Refresh view
        } else {
            window.notificationService.error(_('Error loading card'));
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
        window.notificationService.error(_('Front text is required'));
        elements.editCardFront.focus();
        return;
    }

    if (!backText) {
        window.notificationService.error(_('Back text is required'));
        elements.editCardBack.focus();
        return;
    }

    try {
        // Update card
        await revisionAPI.updateCard(cardId, {
            front_text: frontText,
            back_text: backText
        });

        window.notificationService.success(_('Card updated successfully'));
        
        // Hide form and reload cards
        hideEditCardForm();
        await loadDeckCards();
        
    } catch (error) {
        console.error('Error updating card:', error);
        
        if (error.status === 404) {
            window.notificationService.error(_('This card no longer exists'));
            hideEditCardForm();
            await loadDeckCards(); // Refresh view
        } else if (error.status === 403) {
            window.notificationService.error(_('You do not have permission to edit this card'));
        } else {
            window.notificationService.error(_('Error editing card'));
        }
    }
}

function deleteCard(cardId) {
    showDeleteCardConfirmationModal(cardId);
}

function showDeleteCardConfirmationModal(cardId) {
    // Get card info for display
    const cardElement = document.querySelector(`[data-card-id="${cardId}"]`);
    const frontText = cardElement?.querySelector('.card-front-text')?.textContent || '';
    const backText = cardElement?.querySelector('.card-back-text')?.textContent || '';

    // Truncate text if too long
    const truncate = (text, maxLength = 50) => {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    // Populate modal with card data
    document.getElementById('deleteCardFrontText').textContent = truncate(frontText);
    document.getElementById('deleteCardBackText').textContent = truncate(backText);

    // Show modal using Bootstrap
    const modalElement = document.getElementById('deleteCardModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Set up confirm button handler
    const confirmBtn = document.getElementById('confirmDeleteCardBtn');
    confirmBtn.onclick = () => {
        modal.hide();
        executeDeleteCard(cardId);
    };
}

async function executeDeleteCard(cardId) {
    try {
        await revisionAPI.deleteCard(cardId);

        window.notificationService.success(_('Card deleted successfully'));
        
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
            window.notificationService.warning(_('This card has already been deleted'));
            // Reload the view to reflect current state
            await loadDeckCards();
            await loadDecks();
        } else if (error.status === 403) {
            window.notificationService.error(_('You do not have permission to delete this card'));
        } else {
            window.notificationService.error(_('Error deleting card'));
        }
    }
}

async function createNewDeck() {
    const elements = getElements();
    const name = elements.newDeckName.value.trim();
    const description = elements.newDeckDescription.value.trim();
    const isPublic = elements.newDeckVisibility.value === 'public';
    
    if (!name) {
        window.notificationService.error(_('Deck name is required'));
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
        
        window.notificationService.success(_('Deck created successfully'));
        
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
            window.notificationService.error(_('Error creating deck'));
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

    // Check import type
    const importType = window.getCurrentImportType?.() || 'excel';

    console.log('🚀 Import type:', importType);

    if (importType === 'document') {
        // Handle document import (PDF/Image)
        await handleDocumentImport();
        return;
    }

    // Excel/CSV import (existing logic)
    const file = elements.importFile.files[0] || window.selectedImportFile;
    const name = elements.importDeckName.value.trim();

    console.log('🚀 Import deck - file from input:', elements.importFile.files[0]);
    console.log('🚀 Import deck - file from global:', window.selectedImportFile);
    console.log('🚀 Import deck - using file:', file);

    if (!file) {
        window.notificationService.error('Fichier requis !', 'Veuillez sélectionner un fichier Excel ou CSV avant de continuer.');
        return;
    }
    
    // Vérifier si c'est un import dans un deck existant ou création d'un nouveau deck
    const isImportToExisting = window.importToExistingDeck && window.targetDeckId;
    
    if (!isImportToExisting && !name) {
        window.notificationService.error('Nom d\'une liste requis !', 'Veuillez saisir un nom pour votre liste avant de continuer.');
        // Focus sur le champ nom pour aider l'utilisateur
        elements.importDeckName.focus();
        return;
    }
    
    try {
        // Stocker les infos pour l'étape suivante
        importState.file = file;
        importState.deckName = name;
        
        let targetDeck;
        
        if (isImportToExisting) {
            // Import dans un deck existant
            targetDeck = appState.selectedDeck;
            importState.tempDeck = targetDeck;
            console.log('🔄 Import de cartes dans le deck existant:', targetDeck.name);
        } else {
            // Création d'un nouveau deck
            const deckData = {
                name: name,
                description: _('Deck imported from') + ` ${file.name}`,
                is_public: false
            };
            
            targetDeck = await revisionAPI.createDeck(deckData);
            importState.tempDeck = targetDeck;
            console.log('✨ Nouveau deck créé pour l\'import:', targetDeck.name);
        }
        
        // Then, get preview of the file
        const formData = new FormData();
        formData.append('file', file);
        formData.append('has_header', 'true'); // Initial load always with header
        formData.append('preview_only', 'true');
        formData.append('front_column', '0');
        formData.append('back_column', '1');
        
        const previewResult = await revisionAPI.previewImport(targetDeck.id, formData);
        importState.previewData = previewResult.preview || [];
        importState.columns = previewResult.columns || [];
        
        // Show preview step
        showImportPreview(previewResult);
        
    } catch (error) {
        console.error('Error during preview:', error);
        
        // Gérer les erreurs spécifiques
        if (error.status === 400 && error.message.includes('deck with this name already exists')) {
            window.notificationService.error('Un deck avec ce nom existe déjà. Veuillez choisir un autre nom.');
        } else {
            window.notificationService.error(_('Error preparing import: ') + error.message);
        }
    }
}

// Handle document import (PDF/Image)
async function handleDocumentImport() {
    const elements = getElements();
    const name = elements.importDeckName.value.trim();

    // Check if importing to existing deck or creating new
    const isImportToExisting = window.importToExistingDeck && window.targetDeckId;

    let targetDeck;

    try {
        if (isImportToExisting) {
            // Import to existing deck
            targetDeck = appState.selectedDeck;
            console.log('📄 Document import to existing deck:', targetDeck.name);
        } else {
            // Create new deck
            if (!name) {
                window.notificationService.error('Nom requis', 'Veuillez saisir un nom pour votre liste');
                elements.importDeckName.focus();
                return;
            }

            const deckData = {
                name: name,
                description: 'Deck généré depuis document',
                is_public: false
            };

            targetDeck = await revisionAPI.createDeck(deckData);
            console.log('✨ New deck created for document import:', targetDeck.name);
        }

        // Process document import
        const result = await window.processDocumentImport(targetDeck.id);

        if (result && result.success) {
            // Success - close modal and refresh
            hideImportForm();
            await loadDecks();

            if (targetDeck) {
                selectDeck(targetDeck.id);
            }

            window.notificationService.success(
                _('Success!', 'Succès !'),
                `${result.cards_created} ${_('flashcards generated successfully', 'flashcards générées avec succès')}`
            );
        }

    } catch (error) {
        console.error('❌ Document import error:', error);
        window.notificationService.error(
            _('Error', 'Erreur'),
            _('Error generating flashcards', 'Erreur lors de la génération') + ': ' + error.message
        );
    }
}

// ===== FONCTIONS D'INTERACTIVITÉ AVANCÉE =====

function initializeDragAndDrop() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('importFile');
    
    if (!dropZone || !fileInput) return;
    
    // Marquer comme initialisé pour éviter la duplication
    if (dropZone.dataset.initialized === 'true') {
        console.log('🔄 DragAndDrop déjà initialisé, on passe...');
        return;
    }
    dropZone.dataset.initialized = 'true';
    console.log('🚀 Initialisation DragAndDrop...');
    
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
    dropZone.addEventListener('click', () => {
        console.log('🖱️ Clic sur la zone de drop');
        // Reset juste avant le clic pour permettre la re-sélection
        fileInput.value = '';
        fileInput.click();
    });
    
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
    console.log('handleFileSelect appelé', e);
    console.log('Fichiers sélectionnés:', e.target.files);
    
    const file = e.target.files[0];
    
    if (!file) {
        console.log('No file selected');
        clearSelectedFile();
        return;
    }
    
    console.log('✅ Fichier trouvé:', file.name);
    
    // File validation
    if (!validateFile(file)) {
        console.log('Fichier invalide');
        clearSelectedFile();
        return;
    }
    
    console.log('✅ Fichier valide, affichage des infos');
    
    // Save the file in a temporary global variable
    window.selectedImportFile = file;
    
    // Afficher les informations du fichier
    showSelectedFileInfo(file);
    updateImportButton();
    
    // On ne reset plus automatiquement - on laisse le fichier dans l'input
    // Le reset se fera seulement quand on efface volontairement le fichier
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
        
        // Remplacer d-none par d-block pour Bootstrap
        selectedFileInfo.classList.remove('d-none');
        selectedFileInfo.classList.add('d-block');
        
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
    
    if (selectedFileInfo) {
        selectedFileInfo.classList.remove('d-block');
        selectedFileInfo.classList.add('d-none');
    }
    if (fileInput) fileInput.value = '';
    
    // Nettoyer aussi la variable globale
    window.selectedImportFile = null;
    
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
            const value = this.value.trim();
            // Ne pas montrer d'erreur si le champ est vide et que l'utilisateur n'a pas encore tapé
            const skipEmpty = value === '' && !this.hasAttribute('data-user-interacted');
            if (value !== '' || this.hasAttribute('data-user-interacted')) {
                this.setAttribute('data-user-interacted', 'true');
            }
            validateDeckName(value, skipEmpty);
            updateImportButton();
        }, 300);
    });
    
    // Real-time character counter
    deckNameInput.addEventListener('input', function() {
        updateCharacterCounter(this.value);
    });
}

function validateDeckName(name, skipEmptyValidation = false) {
    const deckNameInput = document.getElementById('importDeckName');
    const errorElement = document.getElementById('deckNameError');
    
    if (!deckNameInput || !errorElement) return false;
    
    // Reset states
    deckNameInput.classList.remove('is-valid', 'is-invalid');
    errorElement.textContent = '';
    
    if (!name) {
        if (!skipEmptyValidation) {
            deckNameInput.classList.add('is-invalid');
            errorElement.textContent = 'Le nom du deck est requis';
        }
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
    
    const hasFile = (fileInput.files && fileInput.files.length > 0) || window.selectedImportFile;
    const deckName = deckNameInput.value.trim();
    
    // Pour updateImportButton, on active TOUJOURS le bouton
    // La validation complète (fichier + nom) se fera au moment du clic
    const isValid = true;
    
    
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
    const estimatedCardsElement = document.getElementById('previewEstimatedCards');
    if (estimatedCardsElement) {
        console.log('Initial load - setting cards to:', estimatedCards);
        estimatedCardsElement.textContent = estimatedCards;
    }
    
    // Afficher les options de colonnes
    const frontSelect = elements.frontColumnSelect;
    const backSelect = elements.backColumnSelect;
    
    frontSelect.innerHTML = '';
    backSelect.innerHTML = '';
    
    const columns = previewResult.columns || [];
    if (columns.length === 0) {
        window.notificationService.error(_('No columns found in file'));
        return;
    }
    
    columns.forEach(col => {
        const optionFront = document.createElement('option');
        optionFront.value = col.index;
        optionFront.textContent = `${_('Column')} ${col.index + 1}: ${col.name || _('Unnamed')}`;
        frontSelect.appendChild(optionFront);
        
        const optionBack = document.createElement('option');
        optionBack.value = col.index;
        optionBack.textContent = `${_('Column')} ${col.index + 1}: ${col.name || _('Unnamed')}`;
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
        
        // Recalculer le nombre de cartes immédiatement, même si les colonnes sont identiques
        const hasHeaderNow = document.getElementById('hasHeaderCheck').checked;
        const totalRowsElement = document.getElementById('previewTotalRows');
        if (totalRowsElement && totalRowsElement.textContent) {
            const totalRows = parseInt(totalRowsElement.textContent) || 0;
            const estimatedCards = Math.max(0, hasHeaderNow ? totalRows - 1 : totalRows);
            const estimatedCardsElement = document.getElementById('previewEstimatedCards');
            if (estimatedCardsElement) {
                console.log('Updating estimated cards:', estimatedCards, 'from total rows:', totalRows, 'hasHeader:', hasHeaderNow);
                estimatedCardsElement.textContent = estimatedCards;
            }
        }
        
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
            // Recalculer le nombre de cartes estimées
            const totalRows = previewResult.total_rows || 0;
            const hasHeaderNow = document.getElementById('hasHeaderCheck').checked;
            const estimatedCards = Math.max(0, hasHeaderNow ? totalRows - 1 : totalRows);
            const estimatedCardsElement = document.getElementById('previewEstimatedCards');
            if (estimatedCardsElement) {
                console.log('Final update - setting cards to:', estimatedCards);
                estimatedCardsElement.textContent = estimatedCards;
            }
            
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
        console.error('Error updating preview:', error);
        window.notificationService.error(_('Error updating preview'));
        
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
        
        // Adapter le message selon le contexte
        const isImportToExisting = window.importToExistingDeck && window.targetDeckId;
        const message = isImportToExisting 
            ? `${importResult.cards_created} ${window.ngettext('card', 'cards', importResult.cards_created)} ajoutées au deck "${importState.tempDeck.name}" !`
            : `Import réussi ! ${importResult.cards_created} ${window.ngettext('card', 'cards', importResult.cards_created)} créées`;
            
        window.notificationService.success(message);
        
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
        
        // Réinitialiser les flags d'import dans deck existant
        window.importToExistingDeck = false;
        window.targetDeckId = null;
        
    } catch (error) {
        console.error('Error during final import:', error);
        window.notificationService.error(_('Import error: ') + error.message);
    }
}

function cancelImportPreview() {
    // TODO: Delete the temporary deck created
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
        window.notificationService.error(_('No deck selected'));
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
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    const elements = getElements();
    const name = elements.editDeckName.value.trim();
    const description = elements.editDeckDescription.value.trim();
    const isPublic = elements.editDeckVisibility.value === 'public';
    
    if (!name) {
        window.notificationService.error(_('Deck name is required'));
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
        
        window.notificationService.success(_('Deck updated successfully'));
        
        // Mettre à jour l'état local
        appState.selectedDeck = updatedDeck;
        
        // Update the deck in the decks list to reflect the changes
        const deckIndex = appState.decks.findIndex(d => d.id === updatedDeck.id);
        if (deckIndex !== -1) {
            appState.decks[deckIndex] = { ...appState.decks[deckIndex], ...updatedDeck };
        }
        
        // Update share button in case visibility changed
        updateShareButtonText();
        
        // Re-render the decks list to show any changes (public icon, name, etc.)
        renderDecksList();
        
        // No need to reload everything, just update the view
        // await loadDecks();
        // await selectDeck(updatedDeck.id);
        
        hideEditDeckForm();
        
    } catch (error) {
        console.error('Error updating deck:', error);
        window.notificationService.error(_('Error editing deck'));
    }
}

// Version de sauvegarde pour auto-save (sans fermer le formulaire)
async function autoSaveEditDeck() {
    if (!appState.selectedDeck) {
        console.error('No deck selected for auto-save');
        return;
    }
    
    const elements = getElements();
    const name = elements.editDeckName.value.trim();
    const description = elements.editDeckDescription.value.trim();
    const isPublic = elements.editDeckVisibility.value === 'public';
    
    if (!name) {
        console.warn('Nom vide, auto-save annulé');
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
        
        console.log('✅ Auto-save successful');
        
        // Mettre à jour l'état local
        appState.selectedDeck = updatedDeck;
        
        // Update the deck in the decks list to reflect the changes
        const deckIndex = appState.decks.findIndex(d => d.id === updatedDeck.id);
        if (deckIndex !== -1) {
            appState.decks[deckIndex] = { ...appState.decks[deckIndex], ...updatedDeck };
        }
        
        // Update share button in case visibility changed
        updateShareButtonText();
        
        // Re-render the decks list to show any changes (public icon, name, etc.)
        renderDecksList();
        
        // Update deck header to show new name
        const deckNameElement = document.getElementById('deckName');
        if (deckNameElement && updatedDeck.name) {
            deckNameElement.textContent = updatedDeck.name;
        }
        const deckDescElement = document.getElementById('deckDescription');
        if (deckDescElement && updatedDeck.description !== undefined) {
            deckDescElement.textContent = updatedDeck.description || _('No description');
        }
        
    } catch (error) {
        console.error('Auto-save error:', error);
        // Ne pas afficher d'erreur pour l'auto-save pour ne pas gêner l'utilisateur
    }
}

// ===== ÉDITION EN PLACE DU NOM ET DESCRIPTION =====

function enableInlineEditDeckName() {
    const deckNameElement = document.getElementById('deckName');
    if (!deckNameElement || !appState.selectedDeck) return;
    
    // Vérifier s'il y a déjà un input en cours d'édition
    if (deckNameElement.parentNode.querySelector('.inline-edit-input')) return;
    
    const currentText = deckNameElement.textContent.trim();
    const originalText = currentText;
    
    // Créer un input temporaire
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentText;
    input.className = 'form-control text-xl font-semibold text-linguify-primary mb-1 inline-edit-input';
    input.style.border = '2px solid #007bff';
    input.style.borderRadius = '4px';
    input.style.padding = '4px 8px';
    input.style.background = '#fff';
    input.style.width = '100%';
    input.style.maxWidth = '400px';
    
    // Fonction de nettoyage et restauration
    const cleanup = () => {
        if (input.parentNode) {
            input.remove();
        }
        deckNameElement.style.display = '';
    };
    
    // Fonction de sauvegarde
    const saveName = async () => {
        const newName = input.value.trim();
        if (newName && newName !== originalText) {
            try {
                const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, {
                    name: newName,
                    description: appState.selectedDeck.description
                });
                appState.selectedDeck.name = newName;
                deckNameElement.textContent = newName;
                
                // Mettre à jour le deck dans la liste des decks
                const deckIndex = appState.decks.findIndex(deck => deck.id === appState.selectedDeck.id);
                if (deckIndex !== -1) {
                    appState.decks[deckIndex].name = newName;
                }
                
                // Rafraîchir la sidebar
                renderDecksList();
                
                window.notificationService.success(_('Deck name updated successfully'));
            } catch (error) {
                console.error('Error updating deck name:', error);
                window.notificationService.error(_('Error editing name'));
                deckNameElement.textContent = originalText;
            }
        } else {
            deckNameElement.textContent = originalText;
        }
        cleanup();
    };
    
    // Fonction d'annulation
    const cancel = () => {
        deckNameElement.textContent = originalText;
        cleanup();
    };
    
    // Event listeners
    input.addEventListener('blur', saveName);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveName();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancel();
        }
    });
    
    // Remplacer l'élément
    deckNameElement.style.display = 'none';
    deckNameElement.parentNode.insertBefore(input, deckNameElement);
    input.focus();
    input.select();
}

function enableInlineEditDeckDescription() {
    const deckDescElement = document.getElementById('deckDescription');
    if (!deckDescElement || !appState.selectedDeck) return;
    
    // Vérifier s'il y a déjà un input en cours d'édition
    if (deckDescElement.parentNode.querySelector('.inline-edit-input')) return;
    
    const currentText = deckDescElement.textContent.trim();
    const originalText = currentText;
    
    // Créer un input temporaire
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentText;
    input.className = 'form-control text-gray-500 inline-edit-input';
    input.style.border = '2px solid #007bff';
    input.style.borderRadius = '4px';
    input.style.padding = '4px 8px';
    input.style.background = '#fff';
    input.style.fontSize = '0.875rem';
    input.style.width = '100%';
    input.style.maxWidth = '600px';
    
    // Fonction de nettoyage et restauration
    const cleanup = () => {
        if (input.parentNode) {
            input.remove();
        }
        deckDescElement.style.display = '';
    };
    
    // Fonction de sauvegarde
    const saveDescription = async () => {
        const newDescription = input.value.trim();
        if (newDescription !== originalText) {
            try {
                const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, {
                    name: appState.selectedDeck.name,
                    description: newDescription
                });
                appState.selectedDeck.description = newDescription;
                deckDescElement.textContent = newDescription;
                
                // Mettre à jour le deck dans la liste des decks
                const deckIndex = appState.decks.findIndex(deck => deck.id === appState.selectedDeck.id);
                if (deckIndex !== -1) {
                    appState.decks[deckIndex].description = newDescription;
                }
                
                // Rafraîchir la sidebar
                renderDecksList();
                
                window.notificationService.success(_('Deck description updated successfully'));
            } catch (error) {
                console.error('Error updating deck description:', error);
                window.notificationService.error(_('Error editing description'));
                deckDescElement.textContent = originalText;
            }
        } else {
            deckDescElement.textContent = originalText;
        }
        cleanup();
    };
    
    // Fonction d'annulation
    const cancel = () => {
        deckDescElement.textContent = originalText;
        cleanup();
    };
    
    // Event listeners
    input.addEventListener('blur', saveDescription);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveDescription();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancel();
        }
    });
    
    // Remplacer l'élément
    deckDescElement.style.display = 'none';
    deckDescElement.parentNode.insertBefore(input, deckDescElement);
    input.focus();
    input.select();
}

function showTagsEditor() {
    if (!appState.selectedDeck) return;
    
    // Open the existing deck edit form
    // qui contient déjà une interface pour gérer les tags
    showEditDeckForm();
    
    // Focus automatiquement sur l'input des tags après un délai
    setTimeout(() => {
        const tagsInput = document.getElementById('editDeckTagsInput');
        if (tagsInput) {
            tagsInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            tagsInput.focus();
        }
    }, 500);
}


function showImportCardsForm() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    // Réutiliser le formulaire d'import existant mais pour import de cartes dans le deck actuel
    hideAllSections();
    
    const elements = getElements();
    elements.importDeckForm.style.display = 'block';
    
    // Clear form
    elements.importFile.value = '';
    // Pré-remplir le nom avec le deck actuel (en lecture seule)
    elements.importDeckName.value = `${appState.selectedDeck.name} (ajout de cartes)`;
    elements.importDeckName.readOnly = true;
    elements.importDeckName.style.backgroundColor = '#f8f9fa';
    
    // Reset validation state
    elements.importDeckName.classList.remove('is-valid', 'is-invalid');
    elements.importDeckName.removeAttribute('data-user-interacted');
    elements.importDeckName.style.borderColor = '#dee2e6';
    elements.importDeckName.style.boxShadow = 'none';
    
    const errorElement = document.getElementById('deckNameError');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
    
    // Changer le titre du formulaire pour indiquer qu'on importe dans un deck existant
    const formTitle = elements.importDeckForm.querySelector('h5');
    if (formTitle) {
        formTitle.textContent = `Importer des cartes dans "${appState.selectedDeck.name}"`;
    }
    
    // Modify the submit button text
    if (elements.submitImport) {
        elements.submitImport.textContent = 'Importer les cartes';
    }
    
    // Stocker l'information que c'est un import de cartes dans un deck existant
    window.importToExistingDeck = true;
    window.targetDeckId = appState.selectedDeck.id;
    
    // Réinitialiser le drag & drop maintenant que le DOM est visible
    setTimeout(() => {
        console.log('🔧 Réinitialisation du drag & drop pour l\'import de cartes');
        initializeDragAndDrop();
        initializeRealTimeValidation();
    }, 100);
}

async function exportDeck() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
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
        
        window.notificationService.success(`Deck exporté : ${cards.length} ${window.ngettext('card', 'cards', cards.length)}`);
        
    } catch (error) {
        console.error('Error exporting deck:', error);
        window.notificationService.error(_('Error exporting deck'));
    }
}

async function makePrivate() {
    console.log('makePrivate called, selectedDeck:', appState.selectedDeck);
    
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    if (!appState.selectedDeck.is_public) {
        window.notificationService.info('Ce deck est déjà privé');
        return;
    }
    
    // Afficher le modal de confirmation personnalisé
    let modalElement = document.getElementById('makePrivateModal');
    
    if (!modalElement) {
        console.log('makePrivateModal not found, creating it dynamically...');
        // Create the modal dynamically
        ensureModalsExist();
        
        // Give a brief moment for DOM to update
        await new Promise(resolve => setTimeout(resolve, 100));
        modalElement = document.getElementById('makePrivateModal');
        
        if (!modalElement) {
            window.notificationService.error('Erreur: Impossible de créer le modal de confirmation');
            return;
        }
    }
    
    console.log('Opening makePrivateModal:', modalElement);
    
    try {
        showTailwindModal(modalElement);
    } catch (error) {
        console.error('Error opening makePrivateModal:', error);
        window.notificationService.error('Erreur lors de l\'ouverture du modal');
    }
}

async function executeMakePrivate() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    try {
        const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, {
            is_public: false
        });
        
        appState.selectedDeck = updatedDeck;
        
        // Update the deck in the decks list to reflect the change
        const deckIndex = appState.decks.findIndex(d => d.id === updatedDeck.id);
        if (deckIndex !== -1) {
            appState.decks[deckIndex] = { ...appState.decks[deckIndex], ...updatedDeck };
        }
        
        // Update the share button text since the deck is now private
        updateShareButtonText();
        
        // Re-render the decks list to hide the public icon
        renderDecksList();
        
        // Close the modal
        const makePrivateModalElement = document.getElementById('makePrivateModal');
        if (makePrivateModalElement) {
            hideTailwindModal(makePrivateModalElement);
        }
        
        window.notificationService.success('Deck rendu privé avec succès');
        
    } catch (error) {
        console.error('Error making deck private:', error);
        window.notificationService.error('Erreur lors de la mise en privé du deck');
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
            showTailwindModal(modalElement);
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
        showTailwindModal(shareModalElement);
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
        // Handler pour le bouton "Make public and share"
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
                
                // Update the deck in the decks list to reflect the change
                const deckIndex = appState.decks.findIndex(d => d.id === updatedDeck.id);
                if (deckIndex !== -1) {
                    appState.decks[deckIndex] = { ...appState.decks[deckIndex], ...updatedDeck };
                }
                
                // Update the share button text since the deck is now public
                updateShareButtonText();
                
                // Re-render the decks list to show the public icon
                renderDecksList();
                
                window.notificationService.success('Jeu de cartes rendu public avec succès !');
                
                // Close current modal and display share modal
                const makePublicModalElement = document.getElementById('makePublicModal');
                if (makePublicModalElement) {
                    hideTailwindModal(makePublicModalElement);
                }
                showShareModal();
                
            } catch (error) {
                console.error('Error making deck public:', error);
                window.notificationService.error('Erreur lors de la publication du jeu de cartes');
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
        
        // Handler pour le bouton "Rendre privé"
        if (e.target.id === 'makeDeckPrivateBtn' || e.target.closest('#makeDeckPrivateBtn')) {
            e.preventDefault();
            const button = e.target.closest('#makeDeckPrivateBtn') || e.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Mise à jour...';
            button.disabled = true;
            
            try {
                await executeMakePrivate();
            } catch (error) {
                console.error('Error making deck private:', error);
                window.notificationService.error('Erreur lors de la mise en privé du deck');
            } finally {
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
                
                // Show success message
                const successMessage = document.getElementById('copySuccessMessage');
                if (successMessage) {
                    successMessage.classList.remove('hidden');
                    setTimeout(() => {
                        successMessage.classList.add('hidden');
                    }, 3000);
                }
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.backgroundColor = 'var(--linguify-primary, #2D5BBA)';
                    button.style.borderColor = 'var(--linguify-primary, #2D5BBA)';
                }, 2000);
                
                window.notificationService.success(_('Link copied to clipboard!'));
            } catch (err) {
                window.notificationService.error('Impossible de copier le lien');
                console.error('Copy failed:', err);
            }
        }
        
        // Handlers pour les nouveaux boutons de partage rapide
        if (e.target.id === 'shareByEmailBtn' || e.target.closest('#shareByEmailBtn')) {
            e.preventDefault();
            const shareUrlInput = document.getElementById('shareUrl');
            if (!shareUrlInput) return;
            shareByEmail(shareUrlInput.value);
        }
        
        if (e.target.id === 'shareByWhatsAppBtn' || e.target.closest('#shareByWhatsAppBtn')) {
            e.preventDefault();
            const shareUrlInput = document.getElementById('shareUrl');
            if (!shareUrlInput) return;
            shareByWhatsApp(shareUrlInput.value);
        }
        
        if (e.target.id === 'shareByMessengerBtn' || e.target.closest('#shareByMessengerBtn')) {
            e.preventDefault();
            const shareUrlInput = document.getElementById('shareUrl');
            if (!shareUrlInput) return;
            shareByMessenger(shareUrlInput.value);
        }
        
        if (e.target.id === 'shareBySMSBtn' || e.target.closest('#shareBySMSBtn')) {
            e.preventDefault();
            const shareUrlInput = document.getElementById('shareUrl');
            if (!shareUrlInput) return;
            shareBySMS(shareUrlInput.value);
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
        case 'reddit':
            shareUrl = `https://reddit.com/submit?title=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
            break;
        default:
            return;
    }
    
    window.open(shareUrl, '_blank', 'width=600,height=400,scrollbars=yes,resizable=yes');
}

// Nouvelles fonctions de partage rapide
function shareByEmail(url) {
    const deckName = appState.selectedDeck.name || 'Jeu de cartes de révision';
    const subject = encodeURIComponent(`Découvrez mon deck de révision: ${deckName}`);
    const body = encodeURIComponent(
        `Salut !\n\n` +
        `Je voulais partager avec toi mon deck de révision "${deckName}" sur OpenLinguify.\n\n` +
        `Tu peux le consulter ici: ${url}\n\n` +
        `Bonne révision ! 📚`
    );
    
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
}

function shareByWhatsApp(url) {
    const deckName = appState.selectedDeck.name || 'Jeu de cartes de révision';
    const text = encodeURIComponent(
        `Salut ! 👋\n\n` +
        `Découvre mon deck de révision "${deckName}" sur OpenLinguify :\n\n` +
        `${url}\n\n` +
        `Parfait pour réviser ! 📚✨`
    );
    
    // Détecter si on est sur mobile ou desktop
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const whatsappUrl = isMobile 
        ? `whatsapp://send?text=${text}`
        : `https://web.whatsapp.com/send?text=${text}`;
        
    window.open(whatsappUrl, '_blank');
}

function shareByMessenger(url) {
    const deckName = appState.selectedDeck.name || 'Jeu de cartes de révision';
    const text = encodeURIComponent(`Découvre mon deck "${deckName}" : ${url}`);
    
    // Facebook Messenger partage
    const messengerUrl = `https://www.messenger.com/new/?text=${text}`;
    window.open(messengerUrl, '_blank');
}

function shareBySMS(url) {
    const deckName = appState.selectedDeck.name || 'Jeu de cartes de révision';
    const text = encodeURIComponent(
        `Salut ! Découvre mon deck de révision "${deckName}" : ${url}`
    );
    
    // Lien SMS universel
    window.location.href = `sms:?body=${text}`;
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
    cardsCountElement.textContent = `${count} ${window.ngettext('card', 'cards', count)}`;
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
        window.notificationService.error(_('Please select at least one language'));
        return;
    }
    
    const confirmMessage = `Voulez-vous appliquer ces langues à toutes les ${appState.selectedDeck.cards_count} ${window.ngettext('card', 'cards', appState.selectedDeck.cards_count)} du deck ?\n\n` +
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
        
        window.notificationService.success(`Langues appliquées à ${deck.cards_count || 0} ${window.ngettext('card', 'cards', deck.cards_count || 0)}`);
        
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
    
    window.notificationService.success(_('Settings applied to new cards'));
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
            window.notificationService.success(_('Language preferences saved'));
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

// Reset Progress functionality
async function resetDeckProgress() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    const deckName = appState.selectedDeck.name;
    const cardsCount = appState.selectedDeck.total_cards || 0;
    
    showResetProgressConfirmationModal(deckName, cardsCount);
}

function showResetProgressConfirmationModal(deckName, cardsCount) {
    // Update modal content with current deck info
    document.getElementById('resetDeckName').textContent = deckName;
    document.getElementById('resetCardCount').textContent = cardsCount;

    // Show the modal using Bootstrap
    const modal = new bootstrap.Modal(document.getElementById('resetProgressModal'));
    modal.show();

    // Set up the confirm button click handler
    document.getElementById('confirmResetProgress').onclick = function() {
        modal.hide();
        window.confirmResetProgress();
    };
}

async function confirmResetProgress() {
    if (!appState.selectedDeck) return;
    
    try {
        // Fermer la modal
        const modal = document.querySelector('.reset-progress-modal');
        if (modal) modal.remove();
        
        // Notification de chargement
        window.notificationService.info(_('Reset in progress...'), 2000);
        
        // Obtenir le CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         document.querySelector('meta[name="csrf-token"]')?.content;
        
        // Appeler l'API
        const response = await fetch(`/api/v1/revision/api/decks/${appState.selectedDeck.id}/reset_progress/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.notificationService.success(data.message || _('Progress reset successfully'));
            
            // Recharger les détails du deck pour rafraîchir l'affichage
            await selectDeck(appState.selectedDeck.id);
            
            // Recharger la liste des decks pour mettre à jour les stats
            await loadDecks(true);
            
        } else {
            window.notificationService.error(_('Error during reset'));
        }
    } catch (error) {
        console.error('Error during reset:', error);
        window.notificationService.error(_('Error during reset') + ': ' + error.message);
    }
}

async function archiveDeck() {
    if (!appState.selectedDeck) {
        window.notificationService.error(_('No deck selected'));
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
        window.notificationService.error(_('No deck selected'));
        return;
    }
    
    try {
        const updatedDeck = await revisionAPI.updateDeck(appState.selectedDeck.id, {
            is_archived: shouldArchive
        });
        
        appState.selectedDeck = updatedDeck;
        
        // Update the deck in the decks list to reflect the change
        const deckIndex = appState.decks.findIndex(d => d.id === updatedDeck.id);
        if (deckIndex !== -1) {
            appState.decks[deckIndex] = { ...appState.decks[deckIndex], ...updatedDeck };
        }
        
        // Update archive button text
        updateArchiveButton();
        
        // Re-render the decks list to show/hide the archive icon
        renderDecksList();
        
        const message = updatedDeck.is_archived ? 'Deck archivé' : 'Deck désarchivé';
        window.notificationService.success(message);
        
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
        window.notificationService.error(_('No deck selected'));
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
    const statusValue = elements.statusFilter.value;
    console.log('🔍 Status filter changed to:', statusValue);
    appState.filters.status = statusValue;
    console.log('🔍 Full filters object:', appState.filters);
    loadDecks();
}

function handleSortFilter() {
    const elements = getElements();
    appState.filters.sort = elements.sortFilter.value;
    loadDecks();
}

// Tags filter functions - now handled entirely by Bootstrap events in setupFilterDropdowns()

// Stats page specific functions
function handleExportStats() {
    try {
        console.log('📊 Exporting statistics...');
        
        // Get current time range
        const timeRange = document.getElementById('statsTimeRange')?.value || '30';
        
        // For now, show a notification that this feature is coming
        if (window.notificationService) {
            window.notificationService.info('Export des statistiques en cours de développement');
        }
        
        // TODO: Implement actual stats export functionality
        // This would typically make an API call to get stats data and download as CSV/JSON
        
    } catch (error) {
        console.error('❌ Error exporting stats:', error);
        if (window.notificationService) {
            window.notificationService.error('Erreur lors de l\'export des statistiques');
        }
    }
}

function handleStatsTimeRangeChange(event) {
    try {
        const selectedRange = event.target.value;
        console.log(`📅 Stats time range changed to: ${selectedRange} days`);
        
        // TODO: Implement stats refresh with new time range
        // This would typically trigger a refresh of the stats dashboard
        
        if (window.notificationService) {
            const rangeText = {
                '7': '7 derniers jours',
                '30': '30 derniers jours', 
                '90': '3 derniers mois',
                '365': 'cette année',
                'all': 'toute la période'
            }[selectedRange] || selectedRange;
            
            window.notificationService.info(`Période mise à jour : ${rangeText}`);
        }
        
    } catch (error) {
        console.error('❌ Error changing stats time range:', error);
    }
}

async function loadTagsFilter() {
    const dropdown = document.getElementById('tagsFilterDropdown');
    
    try {
        // Get tags from loaded decks instead of API call
        const tags = new Set();
        if (appState.decks) {
            appState.decks.forEach(deck => {
                if (deck.tags && Array.isArray(deck.tags)) {
                    deck.tags.forEach(tag => tags.add(tag));
                }
            });
        }
        
        const tagsArray = Array.from(tags).sort();
        
        if (tagsArray.length === 0) {
            const emptyText = dropdown.dataset.emptyText || 'No tags available';
            dropdown.innerHTML = `
                <div class="tags-filter-empty" style="
                    padding: 24px 16px;
                    text-align: center;
                    color: #9ca3af;
                    font-size: 14px;
                ">
                    <i class="bi bi-tags" style="font-size: 24px; margin-bottom: 8px; display: block;"></i>
                    <div>${emptyText}</div>
                </div>
            `;
            return;
        }
        
        dropdown.innerHTML = `
            <li><h6 class="dropdown-header">Filtrer par tags 
                <button onclick="clearTagsFilter()" class="btn btn-sm btn-link p-0 float-end">
                    <i class="bi bi-x-circle"></i>
                </button>
            </h6></li>
            ${tagsArray.map(tag => `
                <li><a class="dropdown-item ${appState.filters.tags.includes(tag) ? 'active' : ''}" 
                       href="#" onclick="toggleTagFilter('${tag}')">
                    <i class="bi ${appState.filters.tags.includes(tag) ? 'bi-check-square' : 'bi-square'} me-2"></i>
                    ${tag}
                </a></li>
            `).join('')}
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
    
    updateTagsFilterText();
    loadDecks();
    loadTagsFilter(); // Refresh the filter display
}

function clearTagsFilter() {
    appState.filters.tags = [];
    updateTagsFilterText();
    loadDecks();
    loadTagsFilter(); // Refresh the filter display
}

function updateTagsFilterText() {
    const textElement = document.getElementById('tagsFilterText');
    const count = appState.filters.tags.length;
    
    if (count === 0) {
        textElement.textContent = 'Tous les tags';
    } else if (count === 1) {
        textElement.textContent = appState.filters.tags[0];
    } else {
        textElement.textContent = `${count} tags`;
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
    
    // Debug pour vérifier la présence de la modal
    const modal = document.getElementById('tagsManagementModal');
    console.log('🔍 Modal tagsManagementModal existe dans le DOM:', !!modal);
    
    // Store the deck ID for the tags management
    // Essayer de charger le gestionnaire de tags de manière robuste
    const loadTagsManager = () => {
        if (window.tagsManagement) {
            console.log('✅ window.tagsManagement trouvé');
            window.tagsManagement.setCurrentDeck(deckId);
            window.tagsManagement.showTagsManagement();
            return true;
        }
        
        // Fallback: Si tagsManagement n'existe pas, essayer de l'initialiser
        if (window.TagsManagement && typeof window.TagsManagement === 'function') {
            console.log('⚡ Initialisation de TagsManagement à la volée');
            window.tagsManagement = new window.TagsManagement();
            window.tagsManagement.init();
            window.tagsManagement.setCurrentDeck(deckId);
            window.tagsManagement.showTagsManagement();
            return true;
        }
        
        // Dernier fallback: Ouvrir la modal directement
        console.warn('⚠️ Fallback: ouverture directe de la modal');
        const modal = document.getElementById('tagsManagementModal');
        if (modal) {
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
            console.log('✅ Modal ouverte directement');
            return true;
        }
        
        return false;
    };
    
    if (!loadTagsManager()) {
        console.error('❌ Impossible d\'ouvrir la gestion des tags');
        console.log('🔍 Objets disponibles:', Object.keys(window).filter(k => k.includes('tags') || k.includes('Tags')));
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
        const response = await window.apiService.request('/api/v1/revision/api/tags/');
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

// Advanced Navbar Error Management System
function showNavbarError(message, severity = 'warning', duration = 5000) {
    try {
        const errorId = `navbar-error-${Date.now()}`;
        const severityClasses = {
            info: 'alert-info',
            warning: 'alert-warning', 
            error: 'alert-danger',
            critical: 'alert-danger border-danger'
        };
        
        const severityIcons = {
            info: 'bi-info-circle',
            warning: 'bi-exclamation-triangle',
            error: 'bi-x-circle', 
            critical: 'bi-shield-exclamation'
        };
        
        // Create error notification
        const errorHtml = `
            <div id="${errorId}" class="alert ${severityClasses[severity]} alert-dismissible fade show position-fixed" 
                 style="top: 80px; right: 20px; z-index: 9999; min-width: 300px; max-width: 500px;">
                <i class="bi ${severityIcons[severity]} me-2"></i>
                <strong>${severity.toUpperCase()}:</strong> ${message}
                <button type="button" class="btn-close" onclick="dismissNavbarError('${errorId}')"></button>
            </div>
        `;
        
        // Inject into DOM
        const existingError = document.getElementById(errorId);
        if (!existingError) {
            document.body.insertAdjacentHTML('beforeend', errorHtml);
            
            // Auto-dismiss after duration
            if (duration > 0) {
                setTimeout(() => dismissNavbarError(errorId), duration);
            }
            
            console.log(`📢 Navbar error shown: [${severity.toUpperCase()}] ${message}`);
        }
        
        // Additional critical error handling
        if (severity === 'critical') {
            // Log to external service (if available)
            if (window.analytics && window.analytics.track) {
                window.analytics.track('Navbar Critical Error', {
                    message, 
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent
                });
            }
            
            // Disable navbar temporarily to prevent cascading errors
            const navbar = document.querySelector('.navbar-linguify');
            if (navbar) {
                navbar.style.pointerEvents = 'none';
                navbar.style.opacity = '0.7';
                
                // Re-enable after 3 seconds
                setTimeout(() => {
                    navbar.style.pointerEvents = '';
                    navbar.style.opacity = '';
                }, 3000);
            }
        }
        
    } catch (errorHandlingError) {
        console.error('❌ Error in error handling system:', errorHandlingError.message);
        // Fallback to basic alert
        alert(`NAVBAR ERROR [${severity}]: ${message}`);
    }
}

function dismissNavbarError(errorId) {
    try {
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.classList.remove('show');
            setTimeout(() => errorElement.remove(), 300);
            console.log(`✅ Error dismissed: ${errorId}`);
        }
    } catch (error) {
        console.error('❌ Error dismissing error notification:', error.message);
    }
}

// Advanced Navbar Health Check System
function performNavbarHealthCheck() {
    const healthReport = {
        timestamp: new Date().toISOString(),
        status: 'healthy',
        issues: [],
        warnings: []
    };
    
    try {
        // Check critical elements
        const criticalElements = [
            'statusFilterToggle',
            'sortFilterToggle', 
            'tagsFilterToggle',
            'searchInput'
        ];
        
        criticalElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (!element) {
                healthReport.issues.push(`Missing critical element: ${elementId}`);
                healthReport.status = 'degraded';
            }
        });
        
        // Check appState integrity
        if (!appState) {
            healthReport.issues.push('appState is undefined');
            healthReport.status = 'critical';
        } else {
            if (!appState.filters) {
                healthReport.issues.push('appState.filters is undefined');
                healthReport.status = 'degraded';
            }
            if (!Array.isArray(appState.decks)) {
                healthReport.warnings.push('appState.decks is not an array');
            }
        }
        
        // Check Bootstrap dependencies
        if (typeof bootstrap === 'undefined') {
            healthReport.warnings.push('Bootstrap JavaScript not loaded');
        }
        
        console.log('🔍 Navbar Health Check:', healthReport);
        
        if (healthReport.issues.length > 0) {
            showNavbarError(
                `Issues détectés: ${healthReport.issues.join(', ')}`, 
                healthReport.status === 'critical' ? 'critical' : 'error'
            );
        }
        
        return healthReport;
        
    } catch (error) {
        console.error('❌ Health check failed:', error.message);
        return { status: 'unknown', error: error.message };
    }
}

// Enhanced Bootstrap Dropdowns with Advanced Error Handling
function setupFilterDropdowns() {
    // Prevent multiple initializations
    if (window.dropdownsInitialized) {
        console.log('🔄 Dropdowns already initialized - skipping setup');
        return;
    }

    try {
        console.log('🔧 Setting up Bootstrap dropdowns with error handling...');
        
        // Perform health check first
        const healthReport = performNavbarHealthCheck();
        
        if (healthReport.status === 'critical') {
            throw new Error('Critical navbar health issues detected');
        }
        
        // Set up Bootstrap dropdown events for tags filter (fixes the re-click issue)
        const tagsToggle = document.getElementById('tagsFilterToggle');
        if (tagsToggle) {
            // Bootstrap event: dropdown is about to be shown
            tagsToggle.addEventListener('show.bs.dropdown', function (event) {
                try {
                    console.log('🏷️ Tags dropdown about to open - loading tags...');
                    loadTagsFilter().catch(error => {
                        console.error('❌ Error loading tags on dropdown open:', error);
                        showNavbarError('Erreur lors du chargement des tags', 'error');
                    });
                } catch (error) {
                    console.error('❌ Error in show.bs.dropdown handler:', error.message);
                    showNavbarError('Erreur lors de l\'ouverture du menu tags', 'error');
                }
            });
            
            // Bootstrap event: dropdown was hidden
            tagsToggle.addEventListener('hidden.bs.dropdown', function (event) {
                console.log('🏷️ Tags dropdown closed');
            });
            
            console.log('✅ Tags dropdown events configured');
        } else {
            console.warn('Tags toggle button not found');
        }
        
        // Set up error resilience for other dropdowns
        ['statusFilterToggle', 'sortFilterToggle'].forEach(toggleId => {
            const toggle = document.getElementById(toggleId);
            if (toggle) {
                toggle.addEventListener('show.bs.dropdown', function (event) {
                    console.log(`📊 ${toggleId} dropdown opening`);
                });
                
                toggle.addEventListener('hidden.bs.dropdown', function (event) {
                    console.log(`📊 ${toggleId} dropdown closed`);
                });
            } else {
                console.warn(`${toggleId} not found`);
            }
        });
        
        // Set up global error catching for dropdown interactions
        document.addEventListener('click', function(event) {
            try {
                const target = event.target;
                if (target.classList.contains('dropdown-item')) {
                    const itemText = target.textContent.trim();
                    console.log('📊 Dropdown item clicked:', itemText);
                    
                    // Gérer les actions spécifiques
                    if (target.id === 'importCards' || itemText === 'Import Cards') {
                        event.preventDefault();
                        console.log('🔧 Calling showImportCardsForm()');
                        if (typeof showImportCardsForm === 'function') {
                            showImportCardsForm();
                        } else {
                            console.error('❌ showImportCardsForm function not found');
                        }
                    }
                }
            } catch (error) {
                console.warn('⚠️ Minor error in dropdown click handler:', error.message);
            }
        });
        
        // Mark as initialized
        window.dropdownsInitialized = true;
        console.log('✅ Bootstrap dropdowns initialized with advanced error handling');
        
    } catch (error) {
        console.error('❌ CRITICAL ERROR in setupFilterDropdowns:', error.message);
        showNavbarError('Erreur critique lors de l\'initialisation des filtres', 'critical');
        
        // Fallback: basic functionality
        console.log('🔄 Attempting basic dropdown fallback...');
        try {
            const tagsToggle = document.querySelector('#tagsFilterToggle');
            if (tagsToggle) {
                tagsToggle.onclick = function() {
                    console.log('🔄 Fallback tags toggle clicked');
                    loadTagsFilter().catch(err => console.error('Fallback error:', err));
                };
            }
        } catch (fallbackError) {
            console.error('❌ Even fallback failed:', fallbackError.message);
        }
    }
}

function selectStatusFilter(value, text) {
    try {
        console.log(`📊 Status filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('statusFilterText');
        const items = document.querySelectorAll('#statusFilterDropdown .dropdown-item');
        
        if (!textElement) {
            throw new Error('Status filter text element not found');
        }
        
        textElement.textContent = text;
        
        // Update selected state with error handling
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('Error updating item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Update app state and reload decks with validation
        if (!appState.filters) {
            console.warn('appState.filters not initialized, creating...');
            appState.filters = {};
        }
        
        appState.filters.status = value;
        loadDecks().catch(error => {
            console.error('❌ Error reloading decks after status filter:', error);
            showNavbarError('Erreur lors de l\'application du filtre', 'error');
        });
        
        console.log('✅ Status filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in selectStatusFilter:', error.message);
        showNavbarError('Erreur lors de la sélection du filtre status', 'error');
    }
}

function selectSortFilter(value, text) {
    try {
        console.log(`📊 Sort filter selected: ${value} (${text})`);
        
        const textElement = document.getElementById('sortFilterText');
        const items = document.querySelectorAll('#sortFilterDropdown .dropdown-item');
        
        if (!textElement) {
            throw new Error('Sort filter text element not found');
        }
        
        textElement.textContent = text;
        
        // Update selected state with error handling
        items.forEach(item => {
            try {
                item.classList.remove('active');
            } catch (itemError) {
                console.warn('Error updating sort item state:', itemError.message);
            }
        });
        
        // Find and mark the selected item
        const selectedItem = Array.from(items).find(item => 
            item.onclick && item.onclick.toString().includes(`'${value}'`)
        );
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Update app state and reload decks with validation
        if (!appState.filters) {
            console.warn('appState.filters not initialized, creating...');
            appState.filters = {};
        }
        
        appState.filters.sort = value;
        loadDecks().catch(error => {
            console.error('❌ Error reloading decks after sort filter:', error);
            showNavbarError('Erreur lors de l\'application du tri', 'error');
        });
        
        console.log('✅ Sort filter applied successfully');
        
    } catch (error) {
        console.error('❌ Error in selectSortFilter:', error.message);
        showNavbarError('Erreur lors de la sélection du tri', 'error');
    }
}

// UI functions
function toggleSidebar() {
    const elements = getElements();
    const isVisible = elements.sidebar.classList.contains('show');

    if (isVisible) {
        // Hide sidebar
        elements.sidebar.classList.remove('show');
        elements.sidebar.style.width = '0px';
        elements.sidebar.style.minWidth = '0px';
        elements.sidebar.style.maxWidth = '0px';
        elements.sidebar.style.padding = '0px';
        elements.sidebar.style.margin = '0px';
        elements.sidebar.style.border = 'none';
        elements.sidebar.style.overflow = 'hidden';
        elements.sidebar.style.flex = '0 0 0px';
        elements.sidebar.style.opacity = '0';
        elements.sidebar.style.visibility = 'hidden';
    } else {
        // Show sidebar
        elements.sidebar.classList.add('show');
        elements.sidebar.style.removeProperty('width');
        elements.sidebar.style.removeProperty('minWidth');
        elements.sidebar.style.removeProperty('maxWidth');
        elements.sidebar.style.removeProperty('padding');
        elements.sidebar.style.removeProperty('margin');
        elements.sidebar.style.removeProperty('border');
        elements.sidebar.style.removeProperty('overflow');
        elements.sidebar.style.removeProperty('flex');
        elements.sidebar.style.removeProperty('opacity');
        elements.sidebar.style.removeProperty('visibility');
    }

    // Update button icon and accessibility attributes based on new state
    const toggleBtn = document.getElementById('toggleSidebar');
    const icon = toggleBtn?.querySelector('i');
    if (icon && toggleBtn) {
        if (isVisible) {
            // Sidebar will be hidden - show "expand" icon
            icon.className = 'bi bi-layout-sidebar-inset-reverse';
            toggleBtn.title = toggleBtn.dataset.showText || 'Afficher la barre latérale';
            toggleBtn.setAttribute('aria-expanded', 'false');
        } else {
            // Sidebar will be shown - show "collapse" icon
            icon.className = 'bi bi-layout-sidebar-inset';
            toggleBtn.title = toggleBtn.dataset.hideText || 'Masquer la barre latérale';
            toggleBtn.setAttribute('aria-expanded', 'true');
        }
    }
}

function backToList() {
    const elements = getElements();
    elements.sidebar.classList.add('show');
    
    // Hide deck details when returning to list
    hideAllSections();
    
    // Show welcome state
    const welcomeState = document.getElementById('welcomeState');
    if (welcomeState) {
        welcomeState.style.display = 'block';
    }
    
    // Clear selected deck from state
    appState.selectedDeck = null;
    
    // Show general actions (create/import buttons)
    updateNavbarActions(true);
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
        refreshDecks: document.getElementById('refreshDecks') || document.getElementById('refreshStats'),
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
    
    // Keyboard shortcut for refresh (F5 or Ctrl+R)
    document.addEventListener('keydown', (event) => {
        // Check if user pressed F5 or Ctrl+R (but not Ctrl+Shift+R which is hard refresh)
        if (event.key === 'F5' || 
            ((event.ctrlKey || event.metaKey) && event.key === 'r' && !event.shiftKey)) {
            
            // Only intercept if we're focused on the revision app (not in input fields)
            const activeElement = document.activeElement;
            const isInInputField = activeElement && (
                activeElement.tagName === 'INPUT' || 
                activeElement.tagName === 'TEXTAREA' || 
                activeElement.contentEditable === 'true'
            );
            
            if (!isInInputField) {
                event.preventDefault(); // Prevent page reload
                console.log('🔄 Raccourci clavier détecté - actualisation...');
                location.reload(); // Simple page refresh for F5 key
            }
        }
    });
    
    // Tags filter - now handled entirely by Bootstrap events in setupFilterDropdowns()
    console.log('Tags filter configured via Bootstrap events in setupFilterDropdowns()');
    
    // Buttons
    elements.createDeck?.addEventListener('click', showCreateForm);
    elements.importDeck?.addEventListener('click', showImportForm);
    // Refresh button now handled by HTMX - no event listener needed
    
    // Handle export stats button
    const exportStatsBtn = document.getElementById('exportStats');
    if (exportStatsBtn) {
        exportStatsBtn.addEventListener('click', handleExportStats);
    }
    
    // Handle stats time range selector
    const statsTimeRange = document.getElementById('statsTimeRange');
    if (statsTimeRange) {
        statsTimeRange.addEventListener('change', handleStatsTimeRangeChange);
    }
    
    elements.backToList?.addEventListener('click', backToList);
    elements.addCard?.addEventListener('click', showCreateCardForm);
    
    // Study mode buttons
    document.getElementById('studyFlashcards')?.addEventListener('click', startFlashcardsMode);
    document.getElementById('studyLearn')?.addEventListener('click', startLearnMode);
    document.getElementById('studyMatch')?.addEventListener('click', startMatchMode);
    document.getElementById('studyReview')?.addEventListener('click', startReviewMode);
    document.getElementById('studyWrite')?.addEventListener('click', startWriteMode);
    
    // Create form
    elements.submitCreate?.addEventListener('click', createNewDeck);
    elements.cancelCreate?.addEventListener('click', hideCreateForm);
    elements.cancelCreateAlt?.addEventListener('click', hideCreateForm);
    
    // Edit deck form
    elements.saveEditDeck?.addEventListener('click', saveEditDeck);
    elements.cancelEditDeck?.addEventListener('click', hideEditDeckForm);
    elements.cancelEditDeckAlt?.addEventListener('click', hideEditDeckForm);
    
    // Auto-save for edit deck form
    if (elements.editDeckName) {
        elements.editDeckName.addEventListener('input', debounce(async () => {
            console.log('🔄 Auto-saving deck name...');
            await autoSaveEditDeck();
        }, 1000));
    }
    if (elements.editDeckDescription) {
        elements.editDeckDescription.addEventListener('input', debounce(async () => {
            console.log('🔄 Auto-saving deck description...');
            await autoSaveEditDeck();
        }, 1000));
    }
    if (elements.editDeckVisibility) {
        elements.editDeckVisibility.addEventListener('change', async () => {
            console.log('🔄 Auto-saving deck visibility...');
            await autoSaveEditDeck();
        });
    }
    
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
    
    // Import cards button - géré par le gestionnaire global des dropdown-item
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
    
    // Make private button
    const makePrivateButton = document.getElementById('makePrivateDeck');
    if (makePrivateButton) {
        makePrivateButton.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Make private button clicked');
            makePrivate();
        });
        console.log('Make private button event listener attached');
    } else {
        console.log('Make private button not found in DOM');
    }
    
    document.getElementById('resetProgress')?.addEventListener('click', resetDeckProgress);
    document.getElementById('archiveDeck')?.addEventListener('click', archiveDeck);
    document.getElementById('deleteDeck')?.addEventListener('click', deleteDeckConfirm);
    
    // Double-click editing for deck name and description
    document.getElementById('deckName')?.addEventListener('dblclick', enableInlineEditDeckName);
    document.getElementById('deckDescription')?.addEventListener('dblclick', enableInlineEditDeckDescription);
    
    // Click on tags to edit
    document.getElementById('deckTagsDisplay')?.addEventListener('click', showTagsEditor);
    
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
    const makePrivateModal = document.getElementById('makePrivateModal');
    
    console.log('Checking modals existence:', {
        makePublicModal: !!makePublicModal,
        shareModal: !!shareModal,
        makePrivateModal: !!makePrivateModal
    });
    
    if (makePublicModal && shareModal && makePrivateModal) {
        console.log('All modals already exist in DOM');
        return;
    }
    
    console.log('Creating modals dynamically...');
    
    // Create makePublicModal with Tailwind
    const makePublicModalHTML = `
        <div class="fixed inset-0 z-50 hidden" id="makePublicModal" aria-hidden="true">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
                <div class="relative bg-white rounded-lg max-w-lg w-full mx-auto shadow-xl">
                    <!-- Header -->
                    <div class="flex items-start justify-between p-6 pb-3">
                        <div class="flex items-center">
                            <div class="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-full mr-4">
                                <i class="bi bi-globe2 text-linguify-primary text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 mb-1">Rendre votre deck public</h3>
                                <p class="text-sm text-gray-500">Permettez à d'autres utilisateurs de le découvrir et l'utiliser</p>
                            </div>
                        </div>
                        <button type="button" class="text-gray-400 hover:text-gray-600" data-bs-dismiss="modal" aria-label="Close">
                            <i class="bi bi-x-lg text-xl"></i>
                        </button>
                    </div>
                    
                    <!-- Body -->
                    <div class="px-6 pb-4">
                        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="bi bi-info-circle-fill text-blue-400 text-lg"></i>
                                </div>
                                <div class="ml-3">
                                    <h4 class="text-sm font-medium text-blue-800">Deck actuellement privé</h4>
                                    <p class="mt-1 text-sm text-blue-700">Ce deck n'est visible que par vous. Rendez-le public pour le partager avec d'autres personnes.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h4 class="flex items-center text-sm font-semibold text-gray-900 mb-3">
                                <i class="bi bi-eye text-blue-600 mr-2"></i>
                                Ce qui se passera en rendant ce deck public :
                            </h4>
                            <ul class="space-y-2">
                                <li class="flex items-start">
                                    <i class="bi bi-check-circle text-green-500 mr-3 mt-0.5 flex-shrink-0"></i>
                                    <span class="text-sm text-gray-700">Il apparaîtra dans la section "Explorer" pour tous</span>
                                </li>
                                <li class="flex items-start">
                                    <i class="bi bi-check-circle text-green-500 mr-3 mt-0.5 flex-shrink-0"></i>
                                    <span class="text-sm text-gray-700">Vous obtiendrez un lien partageable</span>
                                </li>
                                <li class="flex items-start">
                                    <i class="bi bi-check-circle text-green-500 mr-3 mt-0.5 flex-shrink-0"></i>
                                    <span class="text-sm text-gray-700">Vous restez propriétaire et gardez tous vos droits</span>
                                </li>
                            </ul>
                        </div>
                        
                        <div class="flex items-start text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
                            <i class="bi bi-shield-check text-green-500 mr-2 mt-0.5 flex-shrink-0"></i>
                            <span>Vous pourrez toujours rendre votre deck privé plus tard en un clic.</span>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="flex justify-end space-x-3 px-6 py-4 bg-gray-50 rounded-b-lg">
                        <button type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle mr-2"></i>Annuler
                        </button>
                        <button type="button" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" id="makeDeckPublicBtn">
                            <i class="bi bi-globe2 mr-2"></i>${_('Make public')}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Create shareModal with Tailwind
    const shareModalHTML = `
        <div class="fixed inset-0 z-50 hidden" id="shareModal" aria-hidden="true">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
                <div class="relative bg-white rounded-lg max-w-lg w-full mx-auto shadow-xl">
                    <!-- Header -->
                    <div class="flex items-start justify-between p-6 pb-3">
                        <div class="flex items-center">
                            <div class="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mr-4">
                                <i class="bi bi-globe2 text-green-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 mb-1">${_('Share this deck')}</h3>
                                <p class="text-sm text-gray-500" id="shareModalDeckName">"Nom du jeu de cartes"</p>
                            </div>
                        </div>
                        <button type="button" class="text-gray-400 hover:text-gray-600" data-bs-dismiss="modal" aria-label="Close">
                            <i class="bi bi-x-lg text-xl"></i>
                        </button>
                    </div>
                    
                    <!-- Body -->
                    <div class="px-6 pb-4">
                        <p class="mb-4 text-sm text-gray-600">Votre deck est public ! Partagez ce lien avec qui vous voulez :</p>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-900 mb-2">
                                <i class="bi bi-link-45deg mr-2 text-blue-600"></i>Lien de partage
                            </label>
                            <div class="flex">
                                <input type="text" class="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-l-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" readonly id="shareUrl">
                                <button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-blue-600 rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" id="copyShareUrlBtn" type="button">
                                    <i class="bi bi-clipboard mr-1"></i>Copier
                                </button>
                            </div>
                            <div class="mt-1 text-sm text-green-600 hidden" id="copySuccessMessage">
                                <i class="bi bi-check-circle mr-1"></i>Le lien a été copié !
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h4 class="flex items-center text-sm font-semibold text-gray-900 mb-3">
                                <i class="bi bi-send text-blue-600 mr-2"></i>
                                ${_('Share quickly')}
                            </h4>
                            <div class="flex flex-wrap gap-2">
                                <button class="px-3 py-2 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-md hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2" id="shareByEmailBtn" type="button">
                                    <i class="bi bi-envelope mr-1"></i>Email
                                </button>
                                <button class="px-3 py-2 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-md hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2" id="shareByWhatsAppBtn" type="button">
                                    <i class="bi bi-whatsapp mr-1"></i>WhatsApp
                                </button>
                                <button class="px-3 py-2 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" id="shareByMessengerBtn" type="button">
                                    <i class="bi bi-messenger mr-1"></i>Messenger
                                </button>
                                <button class="px-3 py-2 text-xs font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2" id="shareBySMSBtn" type="button">
                                    <i class="bi bi-chat-text mr-1"></i>SMS
                                </button>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h4 class="flex items-center text-sm font-semibold text-gray-900 mb-3">
                                <i class="bi bi-share text-blue-600 mr-2"></i>
                                Réseaux sociaux
                            </h4>
                            <div class="flex flex-wrap gap-2">
                                <button class="px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 social-share-btn" data-platform="twitter" type="button">
                                    <i class="bi bi-twitter mr-1"></i>Twitter
                                </button>
                                <button class="px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 social-share-btn" data-platform="facebook" type="button">
                                    <i class="bi bi-facebook mr-1"></i>Facebook
                                </button>
                                <button class="px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 social-share-btn" data-platform="linkedin" type="button">
                                    <i class="bi bi-linkedin mr-1"></i>LinkedIn
                                </button>
                                <button class="px-3 py-2 text-xs font-medium text-orange-600 bg-orange-50 border border-orange-200 rounded-md hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 social-share-btn" data-platform="reddit" type="button">
                                    <i class="bi bi-reddit mr-1"></i>Reddit
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="flex justify-end px-6 py-4 bg-gray-50 rounded-b-lg">
                        <button type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle mr-2"></i>Fermer
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Create makePrivateModal with Tailwind
    const makePrivateModalHTML = `
        <div class="fixed inset-0 z-50 hidden" id="makePrivateModal" aria-hidden="true">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
                <div class="relative bg-white rounded-lg max-w-lg w-full mx-auto shadow-xl">
                    <!-- Header -->
                    <div class="flex items-start justify-between p-6 pb-3">
                        <div class="flex items-center">
                            <div class="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-full mr-4">
                                <i class="bi bi-lock text-gray-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 mb-1">Rendre votre deck privé</h3>
                                <p class="text-sm text-gray-500">Retirer ce deck de la section publique</p>
                            </div>
                        </div>
                        <button type="button" class="text-gray-400 hover:text-gray-600" data-bs-dismiss="modal" aria-label="Close">
                            <i class="bi bi-x-lg text-xl"></i>
                        </button>
                    </div>
                    
                    <!-- Body -->
                    <div class="px-6 pb-4">
                        <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="bi bi-exclamation-triangle-fill text-amber-400 text-lg"></i>
                                </div>
                                <div class="ml-3">
                                    <h4 class="text-sm font-medium text-amber-800">Attention</h4>
                                    <p class="mt-1 text-sm text-amber-700">Cette action rendra votre deck privé. Il ne sera plus accessible publiquement.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h4 class="flex items-center text-sm font-semibold text-gray-900 mb-3">
                                <i class="bi bi-eye-slash text-amber-500 mr-2"></i>
                                Ce qui va changer :
                            </h4>
                            <ul class="space-y-2">
                                <li class="flex items-start">
                                    <i class="bi bi-x-circle text-red-500 mr-3 mt-0.5 flex-shrink-0"></i>
                                    <span class="text-sm text-gray-700">Il ne sera plus visible dans la section "Explorer"</span>
                                </li>
                                <li class="flex items-start">
                                    <i class="bi bi-x-circle text-red-500 mr-3 mt-0.5 flex-shrink-0"></i>
                                    <span class="text-sm text-gray-700">Les liens de partage existants ne fonctionneront plus</span>
                                </li>
                                <li class="flex items-start">
                                    <i class="bi bi-check-circle text-green-500 mr-3 mt-0.5 flex-shrink-0"></i>
                                    <span class="text-sm text-gray-700">Vous restez propriétaire et gardez tous vos droits</span>
                                </li>
                            </ul>
                        </div>
                        
                        <div class="flex items-start text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
                            <i class="bi bi-shield-check text-green-500 mr-2 mt-0.5 flex-shrink-0"></i>
                            <span>Vous pourrez rendre ce deck public à nouveau plus tard si vous le souhaitez.</span>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="flex justify-end space-x-3 px-6 py-4 bg-gray-50 rounded-b-lg">
                        <button type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle mr-2"></i>Annuler
                        </button>
                        <button type="button" class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-br from-gray-400 to-gray-600 border border-transparent rounded-md shadow-sm hover:from-gray-500 hover:to-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2" id="makeDeckPrivateBtn">
                            <i class="bi bi-lock mr-2"></i>Rendre privé
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modals to DOM
    document.body.insertAdjacentHTML('beforeend', makePublicModalHTML);
    document.body.insertAdjacentHTML('beforeend', shareModalHTML);
    document.body.insertAdjacentHTML('beforeend', makePrivateModalHTML);
    
    console.log('All modals created successfully (including makePrivateModal)');
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
    
    // Setup custom filter dropdowns
    setupFilterDropdowns();
    
    // Initialize view mode
    initializeViewMode();
    
    // Show general actions on app init (no deck selected)
    updateNavbarActions(true);
    
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
    showImportCardsForm,
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
    startWriteMode,
    submitCardEdit,
    hideEditCardForm,
    handleSearch,
    handleStatusFilter,
    handleSortFilter,
    loadMoreDecks,
    toggleSidebar,
    backToList,
    setupEventListeners,
    setupFilterDropdowns,
    initializeApp,
    getElements,
    
    // Advanced Error Management
    showNavbarError,
    dismissNavbarError,
    performNavbarHealthCheck,
    
    
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
    autoSaveEditDeck,
    exportDeck,
    shareDeck,
    enableInlineEditDeckName,
    enableInlineEditDeckDescription,
    showTagsEditor,
    makePrivate,
    executeMakePrivate,
    archiveDeck,
    showArchiveConfirmationModal,
    executeArchiveDeck,
    deleteDeckConfirm,
    showDeleteConfirmationModal,
    executeDeleteDeck,
    
    // Share functions
    showShareModal,
    setupShareModalEventHandlers,
    shareOnSocial,
    shareByEmail,
    shareByWhatsApp,
    shareByMessenger,
    shareBySMS
};

// ===== FONCTIONS UTILITAIRES TAILWIND MODALS =====

function showTailwindModal(modalElement) {
    if (!modalElement) return;
    
    // Remove hidden class and show modal
    modalElement.classList.remove('hidden');
    modalElement.setAttribute('aria-hidden', 'false');
    
    // Add modal-open class to body to prevent scrolling
    document.body.classList.add('overflow-hidden');
    
    // Focus management
    const focusableElement = modalElement.querySelector('button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
    if (focusableElement) {
        setTimeout(() => focusableElement.focus(), 100);
    }
    
    // Handle escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            hideTailwindModal(modalElement);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
    
    // Handle backdrop clicks (the overlay behind the modal)
    const backdrop = modalElement.querySelector('.fixed.inset-0.bg-gray-500');
    if (backdrop) {
        backdrop.addEventListener('click', () => hideTailwindModal(modalElement));
    }
    
    // Handle close buttons
    const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => hideTailwindModal(modalElement));
    });
}

function hideTailwindModal(modalElement) {
    if (!modalElement) return;
    
    // Add hidden class and hide modal
    modalElement.classList.add('hidden');
    modalElement.setAttribute('aria-hidden', 'true');
    
    // Remove modal-open class from body
    document.body.classList.remove('overflow-hidden');
    
    // Clean up event listeners is handled automatically by removing the modal from DOM or using modern event handling
}

// View mode management
function toggleViewMode(mode) {
    console.log('Switching to view mode:', mode);
    
    const listViewBtn = document.getElementById('listViewBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const decksList = document.getElementById('decksList');
    
    if (!listViewBtn || !tableViewBtn || !decksList) {
        console.warn('View toggle elements not found');
        return;
    }
    
    // Update button states
    if (mode === 'list') {
        listViewBtn.classList.add('active');
        tableViewBtn.classList.remove('active');
        
        // Switch to list view
        decksList.classList.remove('table-view');
        decksList.classList.add('list-view');
        
        // Store preference
        localStorage.setItem('decks_view_mode', 'list');
        
    } else if (mode === 'table') {
        tableViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        
        // Switch to table view
        decksList.classList.remove('list-view');
        decksList.classList.add('table-view');
        
        // Store preference
        localStorage.setItem('decks_view_mode', 'table');
    }
    
    console.log('View mode switched to:', mode);
}

// Initialize view mode from stored preference
function initializeViewMode() {
    const savedViewMode = localStorage.getItem('decks_view_mode') || 'list';
    toggleViewMode(savedViewMode);
}

// Export global functions for modal onclick handlers and filter dropdowns
window.confirmResetProgress = confirmResetProgress;
window.selectStatusFilter = selectStatusFilter;
window.selectSortFilter = selectSortFilter;
window.toggleTagFilter = toggleTagFilter;
window.clearTagsFilter = clearTagsFilter;
window.showNavbarError = showNavbarError;
window.dismissNavbarError = dismissNavbarError;
window.selectDeck = selectDeck;
window.toggleViewMode = toggleViewMode;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);