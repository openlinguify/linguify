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
            const allCards = response.results || response || [];
            
            // Need at least 3 cards for matching game
            if (allCards.length < 3) {
                this.showNoCardsMessage();
                return;
            }
            
            // Filter cards that need study (not learned)
            const cardsNeedingReview = allCards.filter(card => !card.learned);
            
            // Use cards that need review, or all cards if none need review
            const cardsToUse = cardsNeedingReview.length > 0 ? cardsNeedingReview : allCards;
            
            // Prepare matching cards (limit to 8 pairs for better UX)
            this.matchingCards = cardsToUse.slice(0, 8);
            
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
        
        // Show matching mode
        document.getElementById('matchingStudyMode').style.display = 'block';
        
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
                 onclick="window.matchingMode.selectItem('${item.id}')">
                <div class="matching-item-content">
                    <div class="matching-item-type">
                        ${item.type === 'term' ? '🔤' : '💡'}
                    </div>
                    <div class="matching-item-text">${item.text}</div>
                </div>
            </div>
        `).join('');
    }

    selectItem(itemId) {
        if (this.gameCompleted) return;
        
        const item = this.matchingItems.find(i => i.id === itemId);
        if (!item) return;
        
        const itemElement = document.querySelector(`[data-id="${itemId}"]`);
        if (!itemElement) return;
        
        // Check if item is already matched
        if (this.matchedPairs.some(pair => pair.includes(item.pairId))) {
            return;
        }
        
        // Check if item is already selected
        if (this.selectedItems.find(selected => selected.id === itemId)) {
            // Deselect item
            this.selectedItems = this.selectedItems.filter(selected => selected.id !== itemId);
            itemElement.classList.remove('selected');
            return;
        }
        
        // Add to selected items
        this.selectedItems.push(item);
        itemElement.classList.add('selected');
        
        // Check if we have 2 selected items
        if (this.selectedItems.length === 2) {
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
            
            // Clear selected items
            this.selectedItems = [];
            
            // Update stats
            this.updateGameStats();
            
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
        document.getElementById('matchingPairs').textContent = this.matchedPairs.length;
        document.getElementById('matchingTotal').textContent = this.matchingCards.length;
        document.getElementById('matchingAttempts').textContent = this.attempts;
        
        // Calculate accuracy
        const accuracy = this.attempts > 0 ? Math.round((this.matchedPairs.length / this.attempts) * 100) : 100;
        document.getElementById('matchingAccuracy').textContent = `${accuracy}%`;
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
            performanceMessage = 'Performance exceptionnelle !';
            performanceClass = 'text-success';
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
                            <div class="stat-value text-success">${this.matchedPairs.length}</div>
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
        document.getElementById('matchingStudyMode').style.display = 'none';
        
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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.matchingMode = new MatchingStudyMode();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MatchingStudyMode;
}