// Revision Quiz Mode (Apprendre)
// Mode questionnaire à choix multiples

class QuizStudyMode {
    constructor() {
        this.currentDeck = null;
        this.quizCards = [];
        this.currentQuestionIndex = 0;
        this.selectedAnswer = null;
        this.hasAnswered = false;
        this.quizStats = {
            correct: 0,
            incorrect: 0,
            total: 0,
            score: 0
        };
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Exit quiz mode
        document.getElementById('exitQuizMode')?.addEventListener('click', () => {
            this.exitQuizMode();
        });
        
        // Next question button
        document.getElementById('nextQuestion')?.addEventListener('click', () => {
            this.nextQuestion();
        });
        
        // Restart quiz
        document.getElementById('restartQuiz')?.addEventListener('click', () => {
            this.restartQuiz();
        });
    }

    async startQuiz(deck) {
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
            const maxCards = userSettings.cards_per_session || 20;
            if (allCards.length > maxCards) {
                console.log(`📊 [Quiz] Limiting session to ${maxCards} cards (from ${allCards.length} total)`);
                // Shuffle first, then limit
                allCards = allCards.sort(() => Math.random() - 0.5).slice(0, maxCards);
            }

            // Need at least 4 cards for multiple choice (1 correct + 3 distractors)
            if (allCards.length < 4) {
                window.notificationService.error('Ce deck doit contenir au moins 4 cartes pour le mode questionnaire');
                return;
            }

            // Prepare quiz cards
            this.quizCards = this.prepareQuizCards(allCards);
            
            if (this.quizCards.length === 0) {
                this.showNoCardsMessage();
                return;
            }
            
            // Reset state
            this.currentQuestionIndex = 0;
            this.selectedAnswer = null;
            this.hasAnswered = false;
            this.resetStats();
            
            // Show quiz interface
            this.showQuizInterface();

            // Use requestAnimationFrame to ensure DOM is updated before loading question
            requestAnimationFrame(() => {
                // Load first question
                this.loadCurrentQuestion();
            });
            
        } catch (error) {
            console.error('Error starting quiz:', error);
            window.notificationService.error('Erreur lors du démarrage du questionnaire');
        }
    }

    prepareQuizCards(cards) {
        // Shuffle cards and prepare quiz questions
        const shuffled = [...cards].sort(() => Math.random() - 0.5);
        
        return shuffled.map(card => ({
            id: card.id,
            question: card.front_text,
            correctAnswer: card.back_text,
            options: this.generateOptions(card, cards),
            learned: card.learned
        }));
    }

    generateOptions(correctCard, allCards) {
        // Get 3 random incorrect answers
        const otherCards = allCards.filter(card => 
            card.id !== correctCard.id && 
            card.back_text !== correctCard.back_text
        );
        
        const incorrectOptions = otherCards
            .sort(() => Math.random() - 0.5)
            .slice(0, 3)
            .map(card => card.back_text);
        
        // Add correct answer and shuffle
        const options = [correctCard.back_text, ...incorrectOptions]
            .sort(() => Math.random() - 0.5);
            
        return options;
    }

    showQuizInterface() {
        // Hide all sections using centralized function
        if (window.revisionMain && window.revisionMain.hideAllSections) {
            window.revisionMain.hideAllSections();
        }
        
        // Show quiz mode with proper flex layout
        const quizElement = document.getElementById('quizStudyMode');
        if (quizElement) {
            quizElement.classList.remove('study-mode-hidden');
            quizElement.style.display = 'flex';
        }
        
        // Set deck name
        document.getElementById('quizDeckName').textContent = this.currentDeck.name;
        
        // Update progress
        this.updateProgress();
        this.updateStats();
    }

    showNoCardsMessage() {
        this.showQuizInterface();
        
        // Hide quiz area and show no cards message
        document.getElementById('quizArea').style.display = 'none';
        document.getElementById('noQuizCards').style.display = 'block';
        
        // Update the message to be more helpful
        const noCardsElement = document.getElementById('noQuizCards');
        noCardsElement.innerHTML = `
            <i class="bi bi-question-circle text-muted" style="font-size: 4rem;"></i>
            <h4 class="mt-3">Pas assez de cartes ou toutes apprises</h4>
            <p class="text-muted">Ce deck doit contenir au moins 4 cartes pour le mode questionnaire.</p>
            <div class="d-flex gap-2 justify-content-center">
                <button class="btn btn-outline-custom" onclick="window.quizMode.practiceAllCards()">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    S'entraîner avec toutes les cartes
                </button>
                <button class="btn btn-gradient" onclick="window.quizMode.exitQuizMode()">
                    Retour au deck
                </button>
            </div>
        `;
    }

    loadCurrentQuestion() {
        if (this.currentQuestionIndex >= this.quizCards.length) {
            this.showQuizCompletion();
            return;
        }

        const quizCard = this.quizCards[this.currentQuestionIndex];

        // Reset state
        this.selectedAnswer = null;
        this.hasAnswered = false;

        // Set question
        const questionElement = document.getElementById('quizQuestion');
        if (!questionElement) {
            console.error('❌ Quiz question element not found in DOM');
            window.notificationService.error('Erreur d\'affichage du questionnaire');
            return;
        }
        questionElement.textContent = quizCard.question;

        // Create options
        const optionsContainer = document.getElementById('quizOptions');
        if (!optionsContainer) {
            console.error('❌ Quiz options container not found in DOM');
            window.notificationService.error('Erreur d\'affichage du questionnaire');
            return;
        }
        optionsContainer.innerHTML = '';
        
        quizCard.options.forEach((option, index) => {
            const optionElement = document.createElement('button');
            optionElement.className = 'quiz-option';
            optionElement.innerHTML = `
                <span class="quiz-option-letter">${String.fromCharCode(65 + index)}</span>
                <span class="quiz-option-text">${option}</span>
            `;
            
            optionElement.addEventListener('click', () => this.selectAnswer(option, optionElement));
            optionsContainer.appendChild(optionElement);
        });
        
        // Hide next button
        document.getElementById('nextQuestion').style.display = 'none';
        
        // Show quiz area
        document.getElementById('quizArea').style.display = 'block';
        document.getElementById('noQuizCards').style.display = 'none';
        
        // Update progress
        this.updateProgress();
    }

    selectAnswer(selectedOption, optionElement) {
        if (this.hasAnswered) return;
        
        this.selectedAnswer = selectedOption;
        this.hasAnswered = true;
        
        const quizCard = this.quizCards[this.currentQuestionIndex];
        const isCorrect = selectedOption === quizCard.correctAnswer;
        
        // Disable all options
        const allOptions = document.querySelectorAll('.quiz-option');
        allOptions.forEach(option => {
            option.disabled = true;
            const optionText = option.querySelector('.quiz-option-text').textContent;
            
            if (optionText === quizCard.correctAnswer) {
                // Mark correct answer
                option.classList.remove('btn-outline-secondary');
                option.classList.add('btn-success');
                option.innerHTML += ' <i class="bi bi-check-circle ms-2"></i>';
            } else if (optionText === selectedOption && !isCorrect) {
                // Mark incorrect selection
                option.classList.remove('btn-outline-secondary');
                option.classList.add('btn-danger');
                option.innerHTML += ' <i class="bi bi-x-circle ms-2"></i>';
            }
        });
        
        // Update stats
        if (isCorrect) {
            this.quizStats.correct++;
            // Update card as learned if it was correct
            this.updateCardProgress(quizCard.id, true);
        } else {
            this.quizStats.incorrect++;
            this.updateCardProgress(quizCard.id, false);
        }
        
        this.updateStats();
        
        // Show next button
        document.getElementById('nextQuestion').style.display = 'inline-block';
        
        // Show feedback
        this.showFeedback(isCorrect, quizCard.correctAnswer);
    }

    showFeedback(isCorrect, correctAnswer) {
        const feedbackElement = document.getElementById('quizFeedback');
        
        if (isCorrect) {
            feedbackElement.innerHTML = `
                <div class="alert alert-success d-flex align-items-center">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <div>
                        <strong>Correct !</strong>
                        <div class="mt-1">Excellente réponse.</div>
                    </div>
                </div>
            `;
        } else {
            feedbackElement.innerHTML = `
                <div class="alert alert-danger d-flex align-items-center">
                    <i class="bi bi-x-circle-fill me-2"></i>
                    <div>
                        <strong>Incorrect</strong>
                        <div class="mt-1">La bonne réponse était : <strong>${correctAnswer}</strong></div>
                    </div>
                </div>
            `;
        }
        
        feedbackElement.style.display = 'block';
    }

    async updateCardProgress(cardId, isCorrect) {
        try {
            await window.revisionMain.revisionAPI.updateCardProgress(cardId, isCorrect);
        } catch (error) {
            console.error('Error updating card progress:', error);
        }
    }

    nextQuestion() {
        // Hide feedback
        document.getElementById('quizFeedback').style.display = 'none';
        
        // Move to next question
        this.currentQuestionIndex++;
        
        if (this.currentQuestionIndex < this.quizCards.length) {
            this.loadCurrentQuestion();
        } else {
            this.showQuizCompletion();
        }
    }

    updateProgress() {
        const progress = document.getElementById('quizProgress');
        const current = this.currentQuestionIndex + 1;
        const total = this.quizCards.length;
        
        if (progress) {
            progress.textContent = `${Math.min(current, total)}/${total}`;
        }
        
        // Update progress bar
        const progressBar = document.getElementById('quizProgressBar');
        if (progressBar) {
            const percentage = (this.currentQuestionIndex / total) * 100;
            progressBar.style.width = `${percentage}%`;
        }
    }

    updateStats() {
        this.quizStats.total = this.quizStats.correct + this.quizStats.incorrect;
        this.quizStats.score = this.quizStats.total > 0 ? 
            Math.round((this.quizStats.correct / this.quizStats.total) * 100) : 0;
        
        document.getElementById('quizCorrect').textContent = this.quizStats.correct;
        document.getElementById('quizIncorrect').textContent = this.quizStats.incorrect;
        document.getElementById('quizScore').textContent = `${this.quizStats.score}%`;
    }

    resetStats() {
        this.quizStats = {
            correct: 0,
            incorrect: 0,
            total: 0,
            score: 0
        };
        this.updateStats();
    }

    showQuizCompletion() {
        const quizArea = document.getElementById('quizArea');
        
        let performanceMessage = '';
        let performanceClass = '';
        
        if (this.quizStats.score >= 80) {
            performanceMessage = 'Excellent travail !';
            performanceClass = 'text-linguify-accent';
        } else if (this.quizStats.score >= 60) {
            performanceMessage = 'Bon travail !';
            performanceClass = 'text-warning';
        } else {
            performanceMessage = 'Continuez à vous entraîner !';
            performanceClass = 'text-danger';
        }
        
        quizArea.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-trophy ${performanceClass}" style="font-size: 4rem;"></i>
                <h4 class="mt-3 ${performanceClass}">${performanceMessage}</h4>
                <p class="text-muted">Quiz terminé ! Voici vos résultats :</p>
                
                <div class="row text-center mt-4 mb-4">
                    <div class="col">
                        <div class="stat-value text-linguify-accent">${this.quizStats.correct}</div>
                        <div class="stat-label">Correctes</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-danger">${this.quizStats.incorrect}</div>
                        <div class="stat-label">Incorrectes</div>
                    </div>
                    <div class="col">
                        <div class="stat-value ${performanceClass}">${this.quizStats.score}%</div>
                        <div class="stat-label">Score</div>
                    </div>
                    <div class="col">
                        <div class="stat-value text-primary">${this.quizStats.total}</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>
                
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-outline-custom" onclick="window.quizMode.restartQuiz()">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Recommencer
                    </button>
                    <button class="btn btn-gradient" onclick="window.quizMode.exitQuizMode()">
                        <i class="bi bi-arrow-left me-1"></i>
                        Retour au deck
                    </button>
                </div>
            </div>
        `;
    }

    async restartQuiz() {
        if (this.currentDeck) {
            await this.startQuiz(this.currentDeck);
        }
    }
    
    async practiceAllCards() {
        if (!this.currentDeck) return;
        
        try {
            // Load ALL cards regardless of learned status
            const response = await window.revisionMain.revisionAPI.getCards(this.currentDeck.id);
            const allCards = response.results || response || [];
            
            // Need at least 4 cards for multiple choice
            if (allCards.length < 4) {
                window.notificationService.error('Ce deck doit contenir au moins 4 cartes pour le mode questionnaire');
                return;
            }
            
            // Prepare quiz cards with all cards
            this.quizCards = this.prepareQuizCards(allCards);
            
            // Reset state
            this.currentQuestionIndex = 0;
            this.selectedAnswer = null;
            this.hasAnswered = false;
            this.resetStats();
            
            // Load first question
            this.loadCurrentQuestion();
            
            // Show notification
            window.notificationService.info('Mode entraînement : questionnaire avec toutes les cartes');
            
        } catch (error) {
            console.error('Error starting quiz practice:', error);
            window.notificationService.error('Erreur lors du démarrage de l\'entraînement');
        }
    }

    exitQuizMode() {
        // Hide quiz mode
        // Hide quiz mode
        const quizElement = document.getElementById('quizStudyMode');
        if (quizElement) {
            quizElement.style.display = 'none';
            quizElement.classList.add('study-mode-hidden');
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
                console.warn('[QuizMode] Could not fetch user settings, using defaults');
                return {
                    cards_per_session: 20,
                    default_session_duration: 20,
                    required_reviews_to_learn: 3
                };
            }

            const data = await response.json();
            console.log('[QuizMode] User settings loaded:', data);
            return data;

        } catch (error) {
            console.error('[QuizMode] Error fetching user settings:', error);
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
    window.quizMode = new QuizStudyMode();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuizStudyMode;
}