// Revision Matching Mode (Associer)
// Jeu de mémoire pour associer les termes et définitions

class MatchingStudyMode {
    constructor() {
        this.currentDeck = null;
        this.matchingCards = [];
        this.matchingItems = [];
        this.selectedItems = [];
        this.matchedPairs = [];
        this.attempts = 0;
        this.startTime = null;
        this.gameCompleted = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Exit matching mode
        document.getElementById('exitMatchingMode')?.addEventListener('click', () => {
            this.exitMatchingMode();
        });
        
        // Restart matching
        document.getElementById('restartMatching')?.addEventListener('click', () => {
            this.restartMatching();
        });
        
        // New game button
        document.getElementById('newMatchingGame')?.addEventListener('click', () => {
            this.startNewGame();
        });
    }

    async startMatching(deck) {
        if (!deck || !deck.id) {
            window.notificationService.error('Deck invalide');
            return;
        }

        try {
            this.currentDeck = deck;
            
            // Load cards for this deck
            const response = await window.revisionMain.revisionAPI.getCards(deck.id);
            let allCards = response.results || response || [];

            // Apply user's session size limit
            const userSettings = await this.getUserSettings();
            const maxCards = Math.min(userSettings.cards_per_session || 20, 12); // Match game works best with max 12 cards
            if (allCards.length > maxCards) {
                console.log(`📊 [Match] Limiting session to ${maxCards} cards (from ${allCards.length} total)`);
                allCards = allCards.sort(() => Math.random() - 0.5).slice(0, maxCards);
            }

            // Need at least 3 cards for matching game
            if (allCards.length < 3) {
                this.showNoCardsMessage();
                return;
            }
            
            // Smart card selection for matching game - prioritize unlearned cards
            const unlearnedCards = allCards.filter(card => !card.learned);
            const learnedCards = allCards.filter(card => card.learned);
            
            console.log(`📊 Cartes disponibles: ${allCards.length} total (${unlearnedCards.length} non-apprises, ${learnedCards.length} apprises)`);
            
            let cardsToUse = [];
            
            // Debug: Show card learning status
            console.log('📋 Détail des cartes:');
            allCards.forEach((card, i) => {
                console.log(`  ${i+1}. "${card.front_text.substring(0, 20)}..." - ${card.learned ? '✅ Apprise' : '❌ Non-apprise'}`);
            });
            
            if (unlearnedCards.length >= 6) {
                // Priorité absolue aux cartes non-apprises (6 cartes)
                cardsToUse = unlearnedCards.slice(0, 6);
                console.log(`🎯 Mode focus: ${cardsToUse.length} ${window.ngettext('card', 'cards', cardsToUse.length)} non-apprises uniquement`);
            } else if (unlearnedCards.length >= 3) {
                // Mélanger cartes non-apprises avec quelques apprises (max 8 total)
                cardsToUse = [...unlearnedCards];
                const needed = Math.min(3, 8 - unlearnedCards.length); // Max 3 cartes apprises
                cardsToUse = cardsToUse.concat(learnedCards.slice(0, needed));
                console.log(`🔄 Mode mixte: ${unlearnedCards.length} non-apprises + ${needed} apprises`);
            } else if (unlearnedCards.length > 0) {
                // Peu de cartes non-apprises, compléter avec apprises
                cardsToUse = [...unlearnedCards];
                cardsToUse = cardsToUse.concat(learnedCards.slice(0, 8 - unlearnedCards.length));
                console.log(`⚖️ Mode équilibré: ${unlearnedCards.length} non-apprises + ${8 - unlearnedCards.length} apprises`);
            } else {
                // Toutes apprises - mode révision (max 6 pour garder de la difficulté)
                cardsToUse = learnedCards.slice(0, 6);
                console.log(`📚 Mode révision: ${cardsToUse.length} ${window.ngettext('card', 'cards', cardsToUse.length)} apprises (révision)`);
            }
            
            // Préparer les cartes matching (mélanger l'ordre)
            this.matchingCards = this.shuffleArray([...cardsToUse]);
            
            // If no cards available after filtering, show practice message
            if (this.matchingCards.length < 3) {
                this.showNoCardsMessage();
                return;
            }
            
            // Reset state
            this.resetGame();
            
            // Show matching interface
            this.showMatchingInterface();
            
            // Start new game
            this.startNewGame();
            
        } catch (error) {
            console.error('Error starting matching game:', error);
            window.notificationService.error('Erreur lors du démarrage du jeu d\'association');
        }
    }

    resetGame() {
        this.selectedItems = [];
        this.matchedPairs = [];
        this.attempts = 0;
        this.startTime = null;
        this.gameCompleted = false;
    }

    showMatchingInterface() {
        // Hide all sections using centralized function
        if (window.revisionMain && window.revisionMain.hideAllSections) {
            window.revisionMain.hideAllSections();
        }
        
        // Show matching mode with proper layout (same as flashcards/quiz)
        const matchingElement = document.getElementById('matchingStudyMode');
        if (matchingElement) {
            matchingElement.classList.remove('study-mode-hidden');
            matchingElement.style.display = 'flex';
        }
        
        // Set deck name
        document.getElementById('matchingDeckName').textContent = this.currentDeck.name;
    }

    showNoCardsMessage() {
        this.showMatchingInterface();
        
        // Hide game area and show no cards message
        document.getElementById('matchingGameArea').style.display = 'none';
        document.getElementById('matchingCompletion').style.display = 'block';
        
        // Update the message to be more helpful
        document.getElementById('matchingCompletionMessage').innerHTML = `
            <div class="text-center">
                <i class="bi bi-puzzle text-muted" style="font-size: 4rem;"></i>
                <h4 class="mt-3">Pas assez de cartes ou toutes apprises</h4>
                <p class="text-muted">Ce deck doit contenir au moins 3 cartes pour le mode association.</p>
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-outline-custom" onclick="window.matchingMode.practiceAllCards()">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        S'entraîner avec toutes les cartes
                    </button>
                    <button class="btn btn-gradient" onclick="window.matchingMode.exitMatchingMode()">
                        Retour au deck
                    </button>
                </div>
            </div>
        `;
    }

    startNewGame() {
        this.resetGame();
        this.startTime = Date.now();
        
        // Create matching items (terms and definitions)
        this.matchingItems = [];
        
        this.matchingCards.forEach((card, index) => {
            // Add term (front)
            this.matchingItems.push({
                id: `term-${index}`,
                cardId: card.id,
                text: card.front_text,
                type: 'term',
                pairId: index
            });
            
            // Add definition (back)
            this.matchingItems.push({
                id: `def-${index}`,
                cardId: card.id,
                text: card.back_text,
                type: 'definition',
                pairId: index
            });
        });
        
        // Shuffle items
        this.matchingItems = this.shuffleArray(this.matchingItems);
        
        // Render game board
        this.renderGameBoard();
        
        // Update stats
        this.updateGameStats();
        
        // Show game area
        document.getElementById('matchingGameArea').style.display = 'block';
        document.getElementById('matchingCompletion').style.display = 'none';
    }

    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    renderGameBoard() {
        const gameBoard = document.getElementById('matchingBoard');
        
        gameBoard.innerHTML = this.matchingItems.map(item => `
            <div class="matching-item ${item.type}" 
                 data-id="${item.id}" 
                 data-pair-id="${item.pairId}"
                 onclick="console.log('Click on item:', '${item.id}'); window.matchingMode.selectItem('${item.id}')">
                <div class="matching-item-content">
                    <div class="matching-item-text">${item.text}</div>
                </div>
            </div>
        `).join('');
        
        // Initialize stats display
        this.updateGameStats();
    }

    selectItem(itemId) {
        console.log('Selecting item:', itemId, 'Game completed:', this.gameCompleted);
        
        if (this.gameCompleted) return;
        
        const item = this.matchingItems.find(i => i.id === itemId);
        if (!item) {
            console.log('Item not found:', itemId);
            return;
        }
        
        const itemElement = document.querySelector(`[data-id="${itemId}"]`);
        if (!itemElement) {
            console.log('Element not found for item:', itemId);
            return;
        }
        
        console.log('Item classes:', itemElement.className);
        console.log('Currently selected items:', this.selectedItems.length);
        
        // Check if item is already matched
        if (itemElement.classList.contains('matched')) {
            console.log('Item already matched, ignoring');
            return;
        }
        
        // Check if item is already selected
        if (this.selectedItems.find(selected => selected.id === itemId)) {
            // Deselect item
            console.log('Deselecting item');
            this.selectedItems = this.selectedItems.filter(selected => selected.id !== itemId);
            itemElement.classList.remove('selected');
            return;
        }
        
        // Add to selected items
        console.log('Adding item to selection');
        this.selectedItems.push(item);
        itemElement.classList.add('selected');
        
        console.log('Selected items count:', this.selectedItems.length);
        
        // Check if we have 2 selected items
        if (this.selectedItems.length === 2) {
            console.log('Two items selected, checking match');
            this.attempts++;
            this.checkMatch();
        }
    }

    checkMatch() {
        const [item1, item2] = this.selectedItems;
        
        if (item1.pairId === item2.pairId && item1.type !== item2.type) {
            // Match found!
            this.handleMatch(item1, item2);
        } else {
            // No match
            this.handleNoMatch(item1, item2);
        }
    }

    handleMatch(item1, item2) {
        // Add to matched pairs
        this.matchedPairs.push(item1.pairId);
        
        // Mark items as matched
        const item1Element = document.querySelector(`[data-id="${item1.id}"]`);
        const item2Element = document.querySelector(`[data-id="${item2.id}"]`);
        
        setTimeout(() => {
            item1Element.classList.remove('selected');
            item2Element.classList.remove('selected');
            item1Element.classList.add('matched');
            item2Element.classList.add('matched');
            
            // Clear selected items immediately
            this.selectedItems = [];
            
            // Update stats
            this.updateGameStats();
            
            console.log('Match successful! Matched pairs:', this.matchedPairs.length, 'Total cards:', this.matchingCards.length);
            
            // Check if game is complete
            if (this.matchedPairs.length === this.matchingCards.length) {
                this.completeGame();
            }
        }, 500);
    }

    handleNoMatch(item1, item2) {
        const item1Element = document.querySelector(`[data-id="${item1.id}"]`);
        const item2Element = document.querySelector(`[data-id="${item2.id}"]`);
        
        // Show error state briefly
        item1Element.classList.add('error');
        item2Element.classList.add('error');
        
        setTimeout(() => {
            item1Element.classList.remove('selected', 'error');
            item2Element.classList.remove('selected', 'error');
            
            // Clear selected items
            this.selectedItems = [];
            
            // Update stats
            this.updateGameStats();
        }, 800);
    }

    updateGameStats() {
        const pairsElement = document.getElementById('matchingPairs');
        const totalElement = document.getElementById('matchingTotal');
        const attemptsElement = document.getElementById('matchingAttempts');
        const accuracyElement = document.getElementById('matchingAccuracy');
        
        if (pairsElement) pairsElement.textContent = this.matchedPairs.length;
        if (totalElement) totalElement.textContent = this.matchingCards.length;
        if (attemptsElement) attemptsElement.textContent = this.attempts;
        
        // Calculate accuracy
        const accuracy = this.attempts > 0 ? Math.round((this.matchedPairs.length / this.attempts) * 100) : 100;
        if (accuracyElement) accuracyElement.textContent = `${accuracy}%`;
        
        console.log('Stats updated:', {
            pairs: this.matchedPairs.length,
            total: this.matchingCards.length,
            attempts: this.attempts,
            accuracy: accuracy
        });
    }

    completeGame() {
        this.gameCompleted = true;
        const endTime = Date.now();
        const timeElapsed = Math.round((endTime - this.startTime) / 1000);
        
        // Calculate performance
        const accuracy = Math.round((this.matchedPairs.length / this.attempts) * 100);
        let performanceMessage = '';
        let performanceClass = '';
        
        if (accuracy >= 90 && timeElapsed <= 60) {
            performanceMessage = 'Excellent';
            performanceClass = 'text-linguify-accent';
        } else if (accuracy >= 70) {
            performanceMessage = 'Bon travail !';
            performanceClass = 'text-warning';
        } else {
            performanceMessage = 'Continuez à vous entraîner !';
            performanceClass = 'text-danger';
        }
        
        // Show completion screen
        setTimeout(() => {
            document.getElementById('matchingGameArea').style.display = 'none';
            document.getElementById('matchingCompletion').style.display = 'block';
            
            document.getElementById('matchingCompletionMessage').innerHTML = `
                <div class="text-center">
                    <i class="bi bi-trophy ${performanceClass}" style="font-size: 4rem;"></i>
                    <h4 class="mt-3 ${performanceClass}">${performanceMessage}</h4>
                    <p class="text-muted">Jeu d'association terminé !</p>
                    
                    <div class="row text-center mt-4 mb-4">
                        <div class="col">
                            <div class="stat-value text-linguify-accent">${this.matchedPairs.length}</div>
                            <div class="stat-label">Paires trouvées</div>
                        </div>
                        <div class="col">
                            <div class="stat-value text-primary">${this.attempts}</div>
                            <div class="stat-label">Tentatives</div>
                        </div>
                        <div class="col">
                            <div class="stat-value ${performanceClass}">${accuracy}%</div>
                            <div class="stat-label">Précision</div>
                        </div>
                        <div class="col">
                            <div class="stat-value text-info">${timeElapsed}s</div>
                            <div class="stat-label">Temps</div>
                        </div>
                    </div>
                </div>
            `;
        }, 1000);
        
        // Update cards as learned
        this.updateCardsLearned();
    }

    async updateCardsLearned() {
        try {
            // Mark all cards as learned since they completed the matching game
            const updatePromises = this.matchingCards.map(card => 
                window.revisionMain.revisionAPI.updateCardProgress(card.id, true)
            );
            
            await Promise.all(updatePromises);
        } catch (error) {
            console.error('Error updating cards learned status:', error);
        }
    }

    async practiceAllCards() {
        if (!this.currentDeck) return;
        
        try {
            // Load ALL cards regardless of learned status
            const response = await window.revisionMain.revisionAPI.getCards(this.currentDeck.id);
            const allCards = response.results || response || [];
            
            // Need at least 3 cards for matching game
            if (allCards.length < 3) {
                window.notificationService.error('Ce deck doit contenir au moins 3 cartes pour le mode association');
                return;
            }
            
            // Use all cards for practice (limit to 8 pairs for better UX)
            this.matchingCards = allCards.slice(0, 8);
            
            // Reset state
            this.resetGame();
            
            // Start new game
            this.startNewGame();
            
            // Show notification
            window.notificationService.info('Mode entraînement : association avec toutes les cartes');
            
        } catch (error) {
            console.error('Error starting matching practice:', error);
            window.notificationService.error('Erreur lors du démarrage de l\'entraînement');
        }
    }

    async restartMatching() {
        if (this.currentDeck) {
            this.startNewGame();
        }
    }

    exitMatchingMode() {
        // Hide matching mode
        const matchingElement = document.getElementById('matchingStudyMode');
        if (matchingElement) {
            matchingElement.style.display = 'none';
            matchingElement.classList.add('study-mode-hidden');
        }
        
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

    async getUserSettings() {
        /**
         * Récupère les paramètres utilisateur depuis l'API
         */
        try {
            const response = await fetch('/api/v1/revision/api/settings/user/', {
                headers: {
                    'X-CSRFToken': window.apiService.getCSRFToken(),
                }
            });

            if (!response.ok) {
                console.warn('[MatchMode] Could not fetch user settings, using defaults');
                return {
                    cards_per_session: 20,
                    default_session_duration: 20,
                    required_reviews_to_learn: 3
                };
            }

            const data = await response.json();
            console.log('[MatchMode] User settings loaded:', data);
            return data;

        } catch (error) {
            console.error('[MatchMode] Error fetching user settings:', error);
            return {
                cards_per_session: 20,
                default_session_duration: 20,
                required_reviews_to_learn: 3
            };
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Initializing MatchingStudyMode...');
    window.matchingMode = new MatchingStudyMode();
    console.log('✅ MatchingStudyMode initialized successfully');
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MatchingStudyMode;
}