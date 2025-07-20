// Revision Spaced Repetition Mode (Révision rapide)
// Révision éclair avec algorithme de répétition espacée

class SpacedRepetitionMode {
    constructor() {
        this.currentDeck = null;
        this.reviewCards = [];
        this.currentCardIndex = 0;
        this.isRevealed = false;
        this.sessionStats = {
            reviewed: 0,
            easy: 0,
            good: 0,
            hard: 0,
            again: 0
        };
        this.startTime = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Exit spaced repetition mode
        document.getElementById('exitSpacedMode')?.addEventListener('click', () => {
            this.exitSpacedMode();
        });
        
        // Reveal answer
        document.getElementById('revealAnswer')?.addEventListener('click', () => {
            this.revealAnswer();
        });
        
        // Difficulty buttons
        document.getElementById('reviewAgain')?.addEventListener('click', () => {
            this.reviewCard('again');
        });
        
        document.getElementById('reviewHard')?.addEventListener('click', () => {
            this.reviewCard('hard');
        });
        
        document.getElementById('reviewGood')?.addEventListener('click', () => {
            this.reviewCard('good');
        });
        
        document.getElementById('reviewEasy')?.addEventListener('click', () => {
            this.reviewCard('easy');
        });
    }

    async startSpacedReview(deck) {
        if (!deck || !deck.id) {
            window.notificationService.error('Deck invalide');
            return;
        }

        try {
            this.currentDeck = deck;
            this.startTime = Date.now();
            
            // Load cards for this deck
            const response = await window.revisionMain.revisionAPI.getCards(deck.id);
            const allCards = response.results || response || [];
            
            // Filter cards that need review based on spaced repetition
            this.reviewCards = this.filterCardsForReview(allCards);
            
            if (this.reviewCards.length === 0) {
                this.showNoReviewNeeded();
                return;
            }
            
            // Sort cards by priority (most urgent first)
            this.reviewCards = this.sortCardsByPriority(this.reviewCards);
            
            // Reset state
            this.currentCardIndex = 0;
            this.isRevealed = false;
            this.resetSessionStats();
            
            // Show spaced repetition interface
            this.showSpacedInterface();
            
            // Load first card
            this.loadCurrentCard();
            
        } catch (error) {
            console.error('Error starting spaced repetition:', error);
            window.notificationService.error('Erreur lors du démarrage de la révision espacée');
        }
    }

    filterCardsForReview(cards) {
        const now = new Date();
        
        const cardsNeedingReview = cards.filter(card => {
            // Include cards that have never been reviewed
            if (!card.last_reviewed) {
                return true;
            }
            
            // Include cards that are due for review
            if (card.next_review) {
                const nextReview = new Date(card.next_review);
                return nextReview <= now;
            }
            
            // Include cards that haven't been learned
            if (!card.learned) {
                return true;
            }
            
            return false;
        });
        
        // If no cards need review, include all cards for practice
        if (cardsNeedingReview.length === 0) {
            return cards;
        }
        
        return cardsNeedingReview;
    }

    sortCardsByPriority(cards) {
        return cards.sort((a, b) => {
            // Priority factors:
            // 1. Cards never reviewed (highest priority)
            // 2. Cards overdue for review
            // 3. Cards with lower review count
            
            const aLastReviewed = a.last_reviewed ? new Date(a.last_reviewed) : null;
            const bLastReviewed = b.last_reviewed ? new Date(b.last_reviewed) : null;
            
            // Never reviewed cards first
            if (!aLastReviewed && bLastReviewed) return -1;
            if (aLastReviewed && !bLastReviewed) return 1;
            if (!aLastReviewed && !bLastReviewed) return 0;
            
            // Then by how overdue they are
            const now = new Date();
            const aNextReview = a.next_review ? new Date(a.next_review) : now;
            const bNextReview = b.next_review ? new Date(b.next_review) : now;
            
            const aOverdue = Math.max(0, now - aNextReview);
            const bOverdue = Math.max(0, now - bNextReview);
            
            if (aOverdue !== bOverdue) {
                return bOverdue - aOverdue; // Most overdue first
            }
            
            // Finally by review count (less reviewed first)
            return (a.review_count || 0) - (b.review_count || 0);
        });
    }

    showSpacedInterface() {
        // Hide all sections using centralized function
        if (window.revisionMain && window.revisionMain.hideAllSections) {
            window.revisionMain.hideAllSections();
        }
        
        // Show spaced repetition mode
        document.getElementById('spacedStudyMode').style.display = 'block';
        
        // Set deck name
        document.getElementById('spacedDeckName').textContent = this.currentDeck.name;
        
        // Update progress
        this.updateProgress();
        this.updateSessionStats();
    }

    showNoReviewNeeded() {
        this.showSpacedInterface();
        
        // Show no review message
        document.getElementById('spacedReviewArea').style.display = 'none';
        document.getElementById('noReviewNeeded').style.display = 'block';
        
        // Update the message to be more helpful
        const noReviewElement = document.getElementById('noReviewNeeded');
        noReviewElement.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-check-circle text-success" style="font-size: 4rem;"></i>
                <h4 class="mt-3 text-success">Aucune carte à réviser !</h4>
                <p class="text-muted">Toutes les cartes sont à jour selon l'algorithme de répétition espacée.</p>
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-outline-custom" onclick="window.spacedMode.practiceAllCards()">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        S'entraîner avec toutes les cartes
                    </button>
                    <button class="btn btn-gradient" onclick="window.spacedMode.exitSpacedMode()">
                        Retour au deck
                    </button>
                </div>
            </div>
        `;
    }

    loadCurrentCard() {
        if (this.currentCardIndex >= this.reviewCards.length) {
            this.showSessionComplete();
            return;
        }

        const card = this.reviewCards[this.currentCardIndex];
        
        // Reset state
        this.isRevealed = false;
        
        // Set card content
        document.getElementById('spacedCardFront').textContent = card.front_text;
        document.getElementById('spacedCardBack').textContent = card.back_text;
        
        // Show question state
        document.getElementById('spacedCardQuestion').style.display = 'block';
        document.getElementById('spacedCardAnswer').style.display = 'none';
        document.getElementById('revealAnswer').style.display = 'inline-block';
        document.getElementById('spacedActions').style.display = 'none';
        
        // Show review area
        document.getElementById('spacedReviewArea').style.display = 'block';
        document.getElementById('noReviewNeeded').style.display = 'none';
        
        // Update progress
        this.updateProgress();
        
        // Show card info
        this.showCardInfo(card);
    }

    showCardInfo(card) {
        const infoElement = document.getElementById('spacedCardInfo');
        
        let reviewInfo = '';
        if (card.last_reviewed) {
            const lastReviewed = new Date(card.last_reviewed);
            const daysSince = Math.floor((Date.now() - lastReviewed) / (1000 * 60 * 60 * 24));
            reviewInfo = `Dernière révision: il y a ${daysSince} jour${daysSince !== 1 ? 's' : ''}`;
        } else {
            reviewInfo = 'Première révision';
        }
        
        const reviewCount = card.review_count || 0;
        
        infoElement.innerHTML = `
            <div class="card-info">
                <small class="text-muted">
                    ${reviewInfo} • Révisée ${reviewCount} fois
                </small>
            </div>
        `;
    }

    revealAnswer() {
        if (this.isRevealed) return;
        
        this.isRevealed = true;
        
        // Show answer
        document.getElementById('spacedCardQuestion').style.display = 'none';
        document.getElementById('spacedCardAnswer').style.display = 'block';
        document.getElementById('revealAnswer').style.display = 'none';
        document.getElementById('spacedActions').style.display = 'flex';
    }

    async reviewCard(difficulty) {
        if (this.currentCardIndex >= this.reviewCards.length) return;
        
        const card = this.reviewCards[this.currentCardIndex];
        
        try {
            // Calculate next review date based on difficulty and current interval
            const { learned, nextReviewDate } = this.calculateNextReview(card, difficulty);
            
            // Update card progress using new API
            const isCorrect = difficulty !== 'again'; // 'again' means incorrect, others are correct
            await window.revisionMain.revisionAPI.updateCardProgress(card.id, isCorrect);
            
            // Update session stats
            this.sessionStats[difficulty]++;
            this.sessionStats.reviewed++;
            
            // Move to next card
            this.currentCardIndex++;
            
            // Update UI
            this.updateSessionStats();
            
            // Load next card or show completion
            if (this.currentCardIndex < this.reviewCards.length) {
                this.loadCurrentCard();
            } else {
                this.showSessionComplete();
            }
            
        } catch (error) {
            console.error('Error reviewing card:', error);
            window.notificationService.error('Erreur lors de la sauvegarde');
        }
    }

    calculateNextReview(card, difficulty) {
        const now = new Date();
        let interval = 1; // Default 1 day
        let learned = false;
        
        const currentReviewCount = (card.review_count || 0) + 1;
        
        switch (difficulty) {
            case 'again':
                interval = 1; // Review again tomorrow
                learned = false;
                break;
                
            case 'hard':
                interval = Math.max(1, Math.floor((currentReviewCount * 1.2)));
                learned = currentReviewCount >= 3;
                break;
                
            case 'good':
                interval = Math.max(1, currentReviewCount * 2);
                learned = currentReviewCount >= 2;
                break;
                
            case 'easy':
                interval = Math.max(3, currentReviewCount * 3);
                learned = true;
                break;
        }
        
        // Cap maximum interval at 30 days
        interval = Math.min(interval, 30);
        
        const nextReviewDate = new Date(now.getTime() + (interval * 24 * 60 * 60 * 1000));
        
        return { learned, nextReviewDate };
    }

    updateProgress() {
        const progress = document.getElementById('spacedProgress');
        const current = this.currentCardIndex + 1;
        const total = this.reviewCards.length;
        
        if (progress) {
            progress.textContent = `${Math.min(current, total)}/${total}`;
        }
        
        // Update progress bar
        const progressBar = document.getElementById('spacedProgressBar');
        if (progressBar) {
            const percentage = total > 0 ? (this.currentCardIndex / total) * 100 : 0;
            progressBar.style.width = `${percentage}%`;
        }
    }

    updateSessionStats() {
        document.getElementById('spacedReviewed').textContent = this.sessionStats.reviewed;
        document.getElementById('spacedRemaining').textContent = Math.max(0, this.reviewCards.length - this.currentCardIndex);
        
        // Calculate session efficiency
        const total = this.sessionStats.reviewed;
        const efficient = this.sessionStats.easy + this.sessionStats.good;
        const efficiency = total > 0 ? Math.round((efficient / total) * 100) : 100;
        document.getElementById('spacedEfficiency').textContent = `${efficiency}%`;
    }

    resetSessionStats() {
        this.sessionStats = {
            reviewed: 0,
            easy: 0,
            good: 0,
            hard: 0,
            again: 0
        };
        this.updateSessionStats();
    }

    showSessionComplete() {
        const endTime = Date.now();
        const timeElapsed = Math.round((endTime - this.startTime) / 1000 / 60); // minutes
        
        const totalReviewed = this.sessionStats.reviewed;
        const efficient = this.sessionStats.easy + this.sessionStats.good;
        const needsWork = this.sessionStats.hard + this.sessionStats.again;
        const efficiency = totalReviewed > 0 ? Math.round((efficient / totalReviewed) * 100) : 100;
        
        let performanceMessage = '';
        let performanceClass = '';
        
        if (efficiency >= 80) {
            performanceMessage = 'Excellente session !';
            performanceClass = 'text-success';
        } else if (efficiency >= 60) {
            performanceMessage = 'Bonne session !';
            performanceClass = 'text-warning';
        } else {
            performanceMessage = 'Continuez vos efforts !';
            performanceClass = 'text-danger';
        }
        
        document.getElementById('spacedReviewArea').style.display = 'none';
        document.getElementById('spacedCompletion').style.display = 'block';
        
        document.getElementById('spacedCompletionMessage').innerHTML = `
            <div class="text-center">
                <i class="bi bi-check-circle ${performanceClass}" style="font-size: 4rem;"></i>
                <h4 class="mt-3 ${performanceClass}">${performanceMessage}</h4>
                <p class="text-muted">Session de révision espacée terminée !</p>
                
                <div class="row text-center mt-4 mb-4">
                    <div class="col">
                        <div class="stat-value text-primary">${totalReviewed}</div>
                        <div class="stat-label">Cartes révisées</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-success">${efficient}</div>
                        <div class="stat-label">Bien maîtrisées</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-warning">${needsWork}</div>
                        <div class="stat-label">À retravailler</div>
                    </div>
                    <div class="col">
                        <div class="stat-value ${performanceClass}">${efficiency}%</div>
                        <div class="stat-label">Efficacité</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-info">${timeElapsed}min</div>
                        <div class="stat-label">Temps</div>
                    </div>
                </div>
                
                <div class="alert alert-info mt-3">
                    <i class="bi bi-lightbulb me-2"></i>
                    Les cartes seront programmées pour révision selon l'algorithme de répétition espacée.
                </div>
                
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-outline-custom" onclick="window.spacedMode.startSpacedReview(window.spacedMode.currentDeck)">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Recommencer
                    </button>
                    <button class="btn btn-gradient" onclick="window.spacedMode.exitSpacedMode()">
                        <i class="bi bi-arrow-left me-1"></i>
                        Retour au deck
                    </button>
                </div>
            </div>
        `;
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
            this.reviewCards = allCards;
            
            // Reset state
            this.currentCardIndex = 0;
            this.isRevealed = false;
            this.resetSessionStats();
            this.startTime = Date.now();
            
            // Load first card
            this.loadCurrentCard();
            
            // Show notification
            window.notificationService.info('Mode entraînement : révision espacée avec toutes les cartes');
            
        } catch (error) {
            console.error('Error starting spaced practice:', error);
            window.notificationService.error('Erreur lors du démarrage de l\'entraînement');
        }
    }

    exitSpacedMode() {
        // Hide spaced repetition mode
        document.getElementById('spacedStudyMode').style.display = 'none';
        
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
    window.spacedMode = new SpacedRepetitionMode();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpacedRepetitionMode;
}