// Revision Flashcards Mode
// Mode de révision avec cartes traditionnelles

class FlashcardStudyMode {
    constructor() {
        this.currentDeck = null;
        this.studyCards = [];
        this.currentCardIndex = 0;
        this.isFlipped = false;
        this.studyStats = {
            correct: 0,
            medium: 0,
            difficult: 0,
            total: 0
        };
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Exit study mode
        document.getElementById('exitStudyMode')?.addEventListener('click', () => {
            this.exitStudyMode();
        });
        
        // Study difficulty buttons
        document.getElementById('studyKnown')?.addEventListener('click', () => {
            this.markCard('easy');
        });
        
        document.getElementById('studyEasy')?.addEventListener('click', () => {
            this.markCard('medium');
        });
        
        document.getElementById('studyDifficult')?.addEventListener('click', () => {
            this.markCard('difficult');
        });
    }

    async startStudy(deck) {
        if (!deck || !deck.id) {
            window.notificationService.error('Deck invalide');
            return;
        }

        try {
            console.log('Starting flashcard study for deck:', deck.name);
            this.currentDeck = deck;
            
            // Load cards for this deck
            console.log('Loading cards for deck ID:', deck.id);
            const response = await window.revisionMain.revisionAPI.getCards(deck.id);
            const allCards = response.results || response || [];
            console.log('Loaded cards:', allCards.length);
            
            // Appliquer d'abord la limite des paramètres utilisateur
            console.log('[FlashcardStudy] About to apply user settings limit...');
            let cardsToStudy;
            try {
                const userSettings = await this.getUserSettings();
                const maxCards = userSettings.cards_per_session || 20;
                console.log(`[FlashcardStudy] User wants ${maxCards} cards per session`);
                
                // Filter cards that need study (not learned or due for review)
                let filteredCards = this.filterCardsForStudy(allCards);
                console.log('Cards to study after filtering:', filteredCards.length);
                
                // Si pas assez de cartes après filtrage, inclure toutes les cartes disponibles
                if (filteredCards.length < maxCards && allCards.length > filteredCards.length) {
                    console.log(`[FlashcardStudy] Not enough filtered cards (${filteredCards.length}), using all available cards (${allCards.length}) to maximize study content`);
                    cardsToStudy = allCards.slice(0, maxCards);
                } else {
                    cardsToStudy = filteredCards.slice(0, maxCards);
                }
                
                console.log('[FlashcardStudy] Successfully applied user settings limit');
            } catch (error) {
                console.error('[FlashcardStudy] Error applying user settings:', error);
                // Fallback au comportement original
                cardsToStudy = this.filterCardsForStudy(allCards).slice(0, 20);
            }
            
            this.studyCards = cardsToStudy;
            console.log('Cards to study after filtering and user settings:', this.studyCards.length);
            
            if (this.studyCards.length === 0) {
                console.log('No cards to study, showing no cards message');
                this.showNoCardsMessage();
                return;
            }
            
            // Reset state
            this.currentCardIndex = 0;
            this.isFlipped = false;
            this.resetStats();
            
            // Show study interface
            console.log('Showing study interface');
            this.showStudyInterface();
            
            // Load first card
            console.log('Loading first card');
            this.loadCurrentCard();
            
        } catch (error) {
            console.error('Error starting flashcard study:', error);
            window.notificationService.error('Erreur lors du démarrage de l\'étude');
        }
    }

    filterCardsForStudy(cards) {
        // First try to get cards that need review
        const cardsNeedingReview = cards.filter(card => {
            // Include cards that are not learned
            if (!card.learned) return true;
            
            // If card has next_review date, check if it's due
            if (card.next_review) {
                const nextReview = new Date(card.next_review);
                const now = new Date();
                return nextReview <= now;
            }
            
            return false;
        });
        
        // If no cards need review, include all cards for practice
        if (cardsNeedingReview.length === 0) {
            return cards; // Return all cards for practice
        }
        
        return cardsNeedingReview;
    }

    showStudyInterface() {
        // Hide all sections using centralized function
        if (window.revisionMain && window.revisionMain.hideAllSections) {
            window.revisionMain.hideAllSections();
        }
        
        // Show flashcard study mode
        document.getElementById('flashcardStudyMode').style.display = 'block';
        
        // Set deck name
        document.getElementById('studyDeckName').textContent = this.currentDeck.name;
        
        // Update progress
        this.updateProgress();
        this.updateStats();
    }

    showNoCardsMessage() {
        this.showStudyInterface();
        
        // Hide study area and show no cards message
        document.getElementById('studyArea').style.display = 'none';
        document.getElementById('noCardsToStudy').style.display = 'block';
        
        // Update the message to be more helpful
        const noCardsElement = document.getElementById('noCardsToStudy');
        noCardsElement.innerHTML = `
            <i class="bi bi-check-circle text-success" style="font-size: 4rem;"></i>
            <h4 class="mt-3 text-success">Aucune carte à réviser !</h4>
            <p class="text-muted">Ce deck ne contient aucune carte, ou alors toutes les cartes sont déjà apprises.</p>
            <div class="d-flex gap-2 justify-content-center">
                <button class="btn btn-outline-custom" onclick="window.flashcardMode.practiceAllCards()">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    S'entraîner avec toutes les cartes
                </button>
                <button class="btn btn-gradient" onclick="window.flashcardMode.exitStudyMode()">
                    Retour au deck
                </button>
            </div>
        `;
    }

    loadCurrentCard() {
        if (this.currentCardIndex >= this.studyCards.length) {
            this.showCompletionMessage();
            return;
        }

        const card = this.studyCards[this.currentCardIndex];
        
        // Reset card state
        this.isFlipped = false;
        const flashcard = document.getElementById('flashcard');
        flashcard.classList.remove('flipped');
        
        // Set card content
        document.getElementById('flashcardFront').textContent = card.front_text;
        document.getElementById('flashcardBack').textContent = card.back_text;
        
        // Hide action buttons initially
        document.getElementById('studyActions').style.display = 'none';
        
        // Show instructions
        document.getElementById('studyInstructions').style.display = 'block';
        
        // Update progress
        this.updateProgress();
    }

    flipCard() {
        if (this.studyCards.length === 0) return;
        
        const flashcard = document.getElementById('flashcard');
        
        if (!this.isFlipped) {
            // Flip to back
            flashcard.classList.add('flipped');
            this.isFlipped = true;
            
            // Show action buttons
            document.getElementById('studyActions').style.display = 'flex';
            document.getElementById('studyInstructions').style.display = 'none';
        }
    }

    async markCard(difficulty) {
        if (this.currentCardIndex >= this.studyCards.length) return;
        
        const card = this.studyCards[this.currentCardIndex];
        console.log('Marking card as:', difficulty, 'Card ID:', card.id);
        
        try {
            // Update card based on difficulty
            let success = false;
            
            switch (difficulty) {
                case 'easy':
                    success = true;
                    this.studyStats.correct++;
                    break;
                case 'medium':
                    success = true;
                    this.studyStats.medium++;
                    break;
                case 'difficult':
                    success = false;
                    this.studyStats.difficult++;
                    break;
            }
            
            console.log('Updating card progress with success:', success);
            // Update card progress using new API
            await window.revisionMain.revisionAPI.updateCardProgress(card.id, success);
            console.log('Card progress updated successfully');
            
            // Mark card as reviewed (you might want to add this to your API)
            // This would update last_reviewed, review_count, next_review
            
            // Move to next card
            this.currentCardIndex++;
            
            // Update stats
            this.updateStats();
            
            // Load next card or show completion
            if (this.currentCardIndex < this.studyCards.length) {
                this.loadCurrentCard();
            } else {
                this.showCompletionMessage();
            }
            
        } catch (error) {
            console.error('Error marking card:', error);
            window.notificationService.error('Erreur lors de la sauvegarde');
        }
    }

    updateProgress() {
        const progress = document.getElementById('studyProgress');
        const remaining = document.getElementById('studyRemaining');
        
        const current = this.currentCardIndex + 1;
        const total = this.studyCards.length;
        
        if (progress) {
            progress.textContent = `${Math.min(current, total)}/${total}`;
        }
        
        if (remaining) {
            remaining.textContent = Math.max(0, total - this.currentCardIndex);
        }
    }

    updateStats() {
        document.getElementById('studyCorrect').textContent = this.studyStats.correct;
        document.getElementById('studyMedium').textContent = this.studyStats.medium;
        document.getElementById('studyDifficult').textContent = this.studyStats.difficult;
        
        this.updateProgress();
    }

    resetStats() {
        this.studyStats = {
            correct: 0,
            medium: 0,
            difficult: 0,
            total: this.studyCards.length
        };
        this.updateStats();
    }

    // Méthode pour récupérer les paramètres utilisateur
    async getUserSettings() {
        try {
            console.log('[FlashcardStudy] Fetching user settings...');
            const response = await fetch('/api/v1/revision/user-settings/');
            
            if (!response.ok) {
                console.warn('[FlashcardStudy] Could not fetch user settings, using defaults');
                return {
                    cards_per_session: 20,
                    default_session_duration: 20,
                    required_reviews_to_learn: 3
                };
            }
            
            const data = await response.json();
            const settings = data.settings || {};
            
            console.log(`[FlashcardStudy] User settings loaded:`, settings);
            return settings;
            
        } catch (error) {
            console.error('[FlashcardStudy] Error fetching user settings:', error);
            return {
                cards_per_session: 20,
                default_session_duration: 20,
                required_reviews_to_learn: 3
            };
        }
    }

    // Nouvelle méthode pour appliquer les paramètres utilisateur (legacy)
    async applyUserSettingsLimit(cards) {
        const settings = await this.getUserSettings();
        const maxCards = settings.cards_per_session || 20;
        console.log(`[FlashcardStudy] Limiting from ${cards.length} to ${Math.min(cards.length, maxCards)} cards`);
        return cards.slice(0, maxCards);
    }

    showCompletionMessage() {
        const studyArea = document.getElementById('studyArea');
        
        // Create completion message
        studyArea.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-trophy text-warning" style="font-size: 4rem;"></i>
                <h4 class="mt-3">Session terminée !</h4>
                <p class="text-muted">Excellent travail ! Vous avez terminé ${this.studyCards.length} cartes.</p>
                <div class="row text-center mt-4 mb-4">
                    <div class="col">
                        <div class="stat-value text-success">${this.studyStats.correct}</div>
                        <div class="stat-label">Faciles</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-warning">${this.studyStats.medium}</div>
                        <div class="stat-label">Moyennes</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-danger">${this.studyStats.difficult}</div>
                        <div class="stat-label">Difficiles</div>
                    </div>
                </div>
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-outline-custom" onclick="window.flashcardMode.restartStudy()">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Recommencer
                    </button>
                    <button class="btn btn-gradient" onclick="window.flashcardMode.exitStudyMode()">
                        <i class="bi bi-arrow-left me-1"></i>
                        Retour au deck
                    </button>
                </div>
            </div>
        `;
    }

    async restartStudy() {
        if (this.currentDeck) {
            await this.startStudy(this.currentDeck);
        }
    }
    
    async practiceAllCards() {
        if (!this.currentDeck) return;
        
        try {
            // Load ALL cards regardless of learned status
            const response = await window.revisionMain.revisionAPI.getCards(this.currentDeck.id);
            const allCards = response.results || response || [];
            
            if (allCards.length === 0) {
                window.notificationService.error('Ce deck ne contient aucune carte');
                return;
            }
            
            // Use all cards for practice
            this.studyCards = allCards;
            
            // Reset state
            this.currentCardIndex = 0;
            this.isFlipped = false;
            this.resetStats();
            
            // Load first card
            this.loadCurrentCard();
            
            // Show notification
            window.notificationService.info('Mode entraînement : révision de toutes les cartes');
            
        } catch (error) {
            console.error('Error starting practice mode:', error);
            window.notificationService.error('Erreur lors du démarrage de l\'entraînement');
        }
    }

    exitStudyMode() {
        // Hide study mode
        document.getElementById('flashcardStudyMode').style.display = 'none';
        
        // Show deck details using centralized function
        if (window.revisionMain.appState.selectedDeck) {
            window.revisionMain.selectDeck(window.revisionMain.appState.selectedDeck.id);
        } else {
            if (window.revisionMain && window.revisionMain.hideAllSections) {
                window.revisionMain.hideAllSections();
            }
            const elements = window.revisionMain.getElements();
            elements.welcomeState.style.display = 'block';
        }
    }
}

// Global function for card flipping (called from HTML)
function flipCard() {
    if (window.flashcardMode) {
        window.flashcardMode.flipCard();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.flashcardMode = new FlashcardStudyMode();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlashcardStudyMode;
}