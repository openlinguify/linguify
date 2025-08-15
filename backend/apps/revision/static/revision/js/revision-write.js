// Write Mode - Mode d'écriture pour réviser en tapant les réponses
class WriteStudyMode {
    constructor() {
        this.currentDeck = null;
        this.studyCards = [];
        this.currentCardIndex = 0;
        this.score = 0;
        this.correctAnswers = 0;
        this.totalAnswers = 0;
        this.hintsUsed = 0;
        this.startTime = null;
        this.timer = null;
        this.timeLimit = 30;
        this.remainingTime = this.timeLimit;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Exit study mode
        document.getElementById('exitWriteStudyMode')?.addEventListener('click', () => {
            this.exitWriteMode();
        });
        
        // Submit answer
        document.getElementById('submitWriteAnswerBtn')?.addEventListener('click', () => {
            this.submitAnswer();
        });
        
        // Enter key to submit
        document.getElementById('writeAnswerInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitAnswer();
            }
        });
        
        // Hint button
        document.getElementById('writeHintBtn')?.addEventListener('click', () => {
            this.showHint();
        });
        
        // Skip button
        document.getElementById('writeSkipBtn')?.addEventListener('click', () => {
            this.skipCard();
        });
        
        // Next card button
        document.getElementById('writeNextBtn')?.addEventListener('click', () => {
            this.nextCard();
        });
        
        // Speak button
        document.getElementById('speakWriteWordBtn')?.addEventListener('click', () => {
            this.speakWord();
        });
    }

    async startWriteStudy(deck) {
        if (!deck || !deck.id) {
            window.notificationService.error('Deck invalide');
            return;
        }

        try {
            console.log('Starting write study for deck:', deck.name);
            this.currentDeck = deck;
            this.startTime = Date.now();
            
            // Load cards for this deck
            const response = await window.revisionMain.revisionAPI.getCards(deck.id);
            const allCards = response.results || response || [];
            console.log('Loaded cards:', allCards.length);
            
            if (allCards.length === 0) {
                window.notificationService.error('Ce deck ne contient aucune carte');
                return;
            }
            
            // Shuffle cards for variety
            this.studyCards = this.shuffleArray([...allCards]);
            
            // Reset state
            this.currentCardIndex = 0;
            this.score = 0;
            this.correctAnswers = 0;
            this.totalAnswers = 0;
            this.hintsUsed = 0;
            
            // Show the write interface
            this.showWriteInterface();
            this.loadCurrentCard();
            this.updateProgress();
            this.startTimer();
            
            console.log(`Write study started with ${this.studyCards.length} cards`);
            
        } catch (error) {
            console.error('Error starting write study:', error);
            window.notificationService.error('Erreur lors du démarrage du mode écriture');
        }
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    showWriteInterface() {
        // Hide all sections using centralized function
        if (window.revisionMain && window.revisionMain.hideAllSections) {
            window.revisionMain.hideAllSections();
        }
        
        // Show write study mode
        const writeElement = document.getElementById('writeStudyMode');
        if (writeElement) {
            writeElement.style.display = 'block';
            writeElement.classList.remove('study-mode-hidden');
        } else {
            console.error('Element writeStudyMode not found');
        }
        
        // Set deck name
        document.getElementById('writeStudyDeckName').textContent = this.currentDeck.name;
        
        // Reset UI state
        this.hideHint();
        this.hideFeedback();
        this.clearInput();
    }

    loadCurrentCard() {
        if (this.currentCardIndex >= this.studyCards.length) {
            this.completeWriteStudy();
            return;
        }

        const currentCard = this.studyCards[this.currentCardIndex];
        
        // Display the word to translate
        document.getElementById('writeWordToTranslate').textContent = currentCard.front_text;
        document.getElementById('writeSourceLanguage').textContent = currentCard.source_language || 'Français';
        
        // Reset UI for new card
        this.hideHint();
        this.hideFeedback();
        this.clearInput();
        this.resetTimer();
        
        // Focus on input
        document.getElementById('writeAnswerInput')?.focus();
        
        this.updateProgress();
    }

    async submitAnswer() {
        const userAnswer = document.getElementById('writeAnswerInput')?.value.trim();
        if (!userAnswer) {
            window.notificationService.warning('Veuillez saisir une réponse');
            return;
        }

        this.stopTimer();
        this.totalAnswers++;
        
        const currentCard = this.studyCards[this.currentCardIndex];
        const correctAnswer = currentCard.back_text;
        const result = this.validateAnswer(userAnswer, correctAnswer);
        
        let isCorrect = false;
        
        // Update score and stats
        if (result === 'correct') {
            this.score += 10;
            this.correctAnswers++;
            isCorrect = true;
            this.showFeedback('success', 'Excellente réponse !', null);
        } else if (result === 'partial') {
            this.score += 5;
            isCorrect = true; // Considérer partiel comme correct pour les stats globales
            this.showFeedback('warning', 'Presque correct ! Vérifiez l\'orthographe.', correctAnswer);
        } else {
            this.showFeedback('danger', 'Incorrect. La bonne réponse était :', correctAnswer);
        }
        
        // Envoyer les résultats au backend pour mettre à jour les stats globales
        await this.updateCardProgress(currentCard.id, isCorrect);
    }

    validateAnswer(userAnswer, correctAnswer) {
        // Normalize both answers
        const normalize = (text) => {
            return text.trim()
                      .toLowerCase()
                      .normalize('NFD')
                      .replace(/[\u0300-\u036f]/g, ''); // Remove accents
        };
        
        const normalizedUser = normalize(userAnswer);
        const normalizedCorrect = normalize(correctAnswer);
        
        // Exact match
        if (normalizedUser === normalizedCorrect) {
            return 'correct';
        }
        
        // Check similarity for partial credit
        const similarity = this.calculateSimilarity(normalizedUser, normalizedCorrect);
        if (similarity >= 0.8) {
            return 'partial';
        }
        
        return 'incorrect';
    }

    calculateSimilarity(str1, str2) {
        // Simple Levenshtein distance based similarity
        const longer = str1.length > str2.length ? str1 : str2;
        const shorter = str1.length > str2.length ? str2 : str1;
        
        if (longer.length === 0) return 1.0;
        
        const distance = this.levenshteinDistance(longer, shorter);
        return (longer.length - distance) / longer.length;
    }

    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }

    showFeedback(type, message, correctAnswer) {
        const feedbackDisplay = document.getElementById('writeFeedbackDisplay');
        const feedbackAlert = document.getElementById('writeFeedbackAlert');
        const feedbackIcon = document.getElementById('writeFeedbackIcon');
        const feedbackMessage = document.getElementById('writeFeedbackMessage');
        const correctAnswerDisplay = document.getElementById('writeCorrectAnswer');
        const correctAnswerText = document.getElementById('writeCorrectAnswerText');
        
        // Reset classes
        feedbackAlert.classList.remove('alert-success', 'alert-warning', 'alert-danger');
        feedbackIcon.classList.remove('bi-check-circle-fill', 'bi-exclamation-triangle-fill', 'bi-x-circle-fill');
        
        // Set appropriate classes based on type
        switch (type) {
            case 'success':
                feedbackAlert.classList.add('alert-success');
                feedbackIcon.classList.add('bi-check-circle-fill');
                break;
            case 'warning':
                feedbackAlert.classList.add('alert-warning');
                feedbackIcon.classList.add('bi-exclamation-triangle-fill');
                break;
            case 'danger':
                feedbackAlert.classList.add('alert-danger');
                feedbackIcon.classList.add('bi-x-circle-fill');
                break;
        }
        
        feedbackMessage.textContent = message;
        
        // Show correct answer if provided
        if (correctAnswer) {
            correctAnswerText.textContent = correctAnswer;
            correctAnswerDisplay.classList.remove('d-none');
        } else {
            correctAnswerDisplay.classList.add('d-none');
        }
        
        feedbackDisplay.classList.remove('d-none');
    }

    hideFeedback() {
        document.getElementById('writeFeedbackDisplay')?.classList.add('d-none');
    }

    showHint() {
        const currentCard = this.studyCards[this.currentCardIndex];
        this.score = Math.max(0, this.score - 2);
        this.hintsUsed++;
        
        // Generate hint (first letter + length)
        const answer = currentCard.back_text;
        const hint = `Le mot commence par "${answer.charAt(0)}" et fait ${answer.length} lettres`;
        
        document.getElementById('writeHintText').textContent = hint;
        document.getElementById('writeHintDisplay').classList.remove('d-none');
        document.getElementById('writeHintBtn').disabled = true;
    }

    hideHint() {
        document.getElementById('writeHintDisplay')?.classList.add('d-none');
        const hintBtn = document.getElementById('writeHintBtn');
        if (hintBtn) {
            hintBtn.disabled = false;
        }
    }

    async skipCard() {
        this.score = Math.max(0, this.score - 5);
        this.totalAnswers++;
        this.stopTimer();
        
        const currentCard = this.studyCards[this.currentCardIndex];
        this.showFeedback('danger', 'Carte passée. La bonne réponse était :', currentCard.back_text);
        
        // Envoyer comme réponse incorrecte au backend
        await this.updateCardProgress(currentCard.id, false);
    }

    nextCard() {
        this.currentCardIndex++;
        this.loadCurrentCard();
    }

    clearInput() {
        const input = document.getElementById('writeAnswerInput');
        if (input) {
            input.value = '';
        }
    }

    startTimer() {
        this.remainingTime = this.timeLimit;
        this.updateTimerDisplay();
        
        this.timer = setInterval(() => {
            this.remainingTime--;
            this.updateTimerDisplay();
            
            if (this.remainingTime <= 0) {
                this.stopTimer();
                this.skipCard();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    resetTimer() {
        this.stopTimer();
        this.startTimer();
    }

    updateTimerDisplay() {
        const timerElement = document.getElementById('writeTimer');
        if (timerElement) {
            timerElement.textContent = `${this.remainingTime}s`;
            
            // Change color based on remaining time
            timerElement.classList.remove('bg-info', 'bg-warning', 'bg-danger');
            if (this.remainingTime > 15) {
                timerElement.classList.add('bg-info');
            } else if (this.remainingTime > 5) {
                timerElement.classList.add('bg-warning');
            } else {
                timerElement.classList.add('bg-danger');
            }
        }
    }

    updateProgress() {
        const progressElement = document.getElementById('writeStudyProgress');
        const progressBar = document.getElementById('writeProgressBar');
        
        const current = this.currentCardIndex + 1;
        const total = this.studyCards.length;
        const percentage = (current / total) * 100;
        
        if (progressElement) {
            progressElement.textContent = `${Math.min(current, total)}/${total}`;
        }
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
    }

    speakWord() {
        const currentCard = this.studyCards[this.currentCardIndex];
        if (currentCard && 'speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(currentCard.front_text);
            utterance.lang = 'fr-FR';
            speechSynthesis.speak(utterance);
        }
    }

    completeWriteStudy() {
        this.stopTimer();
        
        const totalTime = Math.round((Date.now() - this.startTime) / 1000);
        const accuracy = this.totalAnswers > 0 ? Math.round((this.correctAnswers / this.totalAnswers) * 100) : 0;
        
        // Update modal with results
        document.getElementById('writeCorrectCount').textContent = this.correctAnswers;
        document.getElementById('writeTotalScore').textContent = this.score;
        document.getElementById('writeHintsUsed').textContent = this.hintsUsed;
        document.getElementById('writeAccuracy').textContent = `${accuracy}%`;
        
        const minutes = Math.floor(totalTime / 60);
        const seconds = totalTime % 60;
        document.getElementById('writeTotalTime').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Show completion modal
        if (typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(document.getElementById('writeCompletionModal'));
            modal.show();
        }
        
        console.log(`Write study completed! Score: ${this.score}, Accuracy: ${accuracy}%`);
    }

    exitWriteMode() {
        this.stopTimer();
        
        // Hide write study mode
        const writeElement = document.getElementById('writeStudyMode');
        if (writeElement) {
            writeElement.style.display = 'none';
            writeElement.classList.add('study-mode-hidden');
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

    restart() {
        if (this.currentDeck) {
            this.startWriteStudy(this.currentDeck);
        }
    }

    async updateCardProgress(cardId, isCorrect) {
        /**
         * Met à jour les statistiques de la carte dans le backend
         */
        try {
            const response = await window.apiService.request(
                `/api/v1/revision/flashcards/${cardId}/update_review_progress/`,
                {
                    method: 'POST',
                    body: JSON.stringify({
                        is_correct: isCorrect
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );
            
            console.log(`✅ Stats mises à jour pour la carte ${cardId}: ${isCorrect ? 'correct' : 'incorrect'}`);
            return response;
            
        } catch (error) {
            console.error(`❌ Erreur lors de la mise à jour des stats pour la carte ${cardId}:`, error);
            // Ne pas bloquer l'exercice si l'API échoue
            return null;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.writeMode = new WriteStudyMode();
    console.log('Write study mode initialized');
});