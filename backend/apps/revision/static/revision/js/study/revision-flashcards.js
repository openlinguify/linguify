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
        // Synthèse vocale
        this.speechSynthesis = window.speechSynthesis;
        this.currentUtterance = null;
        this.voices = [];
        this.setupEventListeners();
        this.initializeSpeechSynthesis();
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
            
            // Load cards for this deck using smart spaced repetition algorithm
            console.log('Loading cards for deck ID:', deck.id);
            const response = await window.revisionMain.revisionAPI.getCards(deck.id, {
                studyMode: 'smart',
                mixedOrder: true,
                prioritizeOverdue: true
            });
            
            // Handle smart mode response structure
            const allCards = response.cards || response.results || response || [];
            const studySession = response.study_session || null;
            console.log('Loaded cards:', allCards.length);
            
            // Log spaced repetition information if available
            if (studySession) {
                console.log('Smart study session data:', studySession);
                if (studySession.recommendations?.length > 0) {
                    console.log('Study recommendations:', studySession.recommendations);
                }
            }
            
            // Check if we're using smart mode (cards already intelligently selected)
            let cardsToStudy;
            if (studySession && studySession.study_mode === 'smart') {
                // Smart mode: use cards exactly as provided by the spaced repetition algorithm
                console.log('[FlashcardStudy] Using smart mode - cards already optimally selected by algorithm');
                cardsToStudy = allCards; // These are already filtered and prioritized by the algorithm
            } else {
                // Legacy mode: apply manual filtering
                console.log('[FlashcardStudy] Using legacy mode - applying manual filtering...');
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
        console.log('🎯 showStudyInterface called');
        
        // Hide all sections using centralized function
        if (window.revisionMain && window.revisionMain.hideAllSections) {
            console.log('📦 Calling hideAllSections...');
            window.revisionMain.hideAllSections();
        }
        
        // Check if flashcard element exists
        const flashcardElement = document.getElementById('flashcardStudyMode');
        console.log('🔍 flashcardStudyMode element:', flashcardElement);
        console.log('🔍 flashcardStudyMode exists:', !!flashcardElement);
        
        if (flashcardElement) {
            console.log('✅ Removing study-mode-hidden class and setting display to flex...');
            // Remove the hidden class that forces display: none !important
            flashcardElement.classList.remove('study-mode-hidden');
            // Set the display style
            flashcardElement.style.display = 'flex';
            console.log('🎨 Element style after setting:', flashcardElement.style.display);
            console.log('🎨 Element computed style:', window.getComputedStyle(flashcardElement).display);
            console.log('🏷️ Element classes:', flashcardElement.className);
        } else {
            console.error('❌ flashcardStudyMode element not found in DOM!');
            return;
        }
        
        // Set deck name
        const deckNameElement = document.getElementById('studyDeckName');
        if (deckNameElement && this.currentDeck) {
            deckNameElement.textContent = this.currentDeck.name;
            console.log('📝 Deck name set to:', this.currentDeck.name);
        }
        
        // Update progress
        this.updateProgress();
        this.updateStats();
        
        console.log('🎯 showStudyInterface completed');
    }

    showNoCardsMessage() {
        this.showStudyInterface();
        
        // Hide study area and show no cards message
        document.getElementById('studyArea').style.display = 'none';
        document.getElementById('noCardsToStudy').style.display = 'block';
        
        // Update the message to be more helpful
        const noCardsElement = document.getElementById('noCardsToStudy');
        noCardsElement.innerHTML = `
            <i class="bi bi-check-circle text-linguify-accent" style="font-size: 4rem;"></i>
            <h4 class="mt-3 text-linguify-accent">${window.translations['No cards to review!'] || 'Aucune carte à réviser !'}</h4>
            <p class="text-muted">${window.translations['This deck contains no cards, or all cards are already learned.'] || 'Ce deck ne contient aucune carte, ou alors toutes les cartes sont déjà apprises.'}</p>
            <div class="d-flex gap-2 justify-content-center">
                <button class="btn btn-outline-custom" id="practiceAllCardsBtn">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    ${window.translations['Practice with all cards'] || "S'entraîner avec toutes les cartes"}
                </button>
                <button class="btn btn-gradient" id="exitFromNoCardsBtn">
                    ${window.translations['Back to deck'] || 'Retour au deck'}
                </button>
            </div>
        `;
        
        // Add event listeners for the no cards message buttons
        setTimeout(() => {
            const practiceBtn = document.getElementById('practiceAllCardsBtn');
            const exitBtn = document.getElementById('exitFromNoCardsBtn');
            
            if (practiceBtn) {
                practiceBtn.addEventListener('click', () => {
                    console.log('Practice all cards button clicked');
                    this.practiceAllCards();
                });
            }
            
            if (exitBtn) {
                exitBtn.addEventListener('click', () => {
                    console.log('Exit from no cards button clicked');
                    this.exitStudyMode();
                });
            }
        }, 100); // Small delay to ensure DOM is updated
    }

    loadCurrentCard() {
        if (this.currentCardIndex >= this.studyCards.length) {
            this.showCompletionMessage();
            return;
        }

        // Stop any ongoing speech when loading a new card
        this.stopSpeech();

        const card = this.studyCards[this.currentCardIndex];
        
        // Reset card state
        this.isFlipped = false;
        const flashcard = document.getElementById('flashcard');
        if (flashcard) {
            flashcard.classList.remove('flipped');
        }
        
        // Set card content
        const frontElement = document.getElementById('flashcardFront');
        const backElement = document.getElementById('flashcardBack');
        const actionsElement = document.getElementById('studyActions');
        const instructionsElement = document.getElementById('studyInstructions');
        
        if (frontElement) frontElement.textContent = card.front_text;
        if (backElement) backElement.textContent = card.back_text;
        
        // Hide action buttons initially
        if (actionsElement) actionsElement.style.display = 'none';
        
        // Show instructions
        if (instructionsElement) instructionsElement.style.display = 'block';
        
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
        } else {
            // Flip back to front
            flashcard.classList.remove('flipped');
            this.isFlipped = false;

            // Keep action buttons visible (user can still flip back and forth before answering)
            // Instructions stay hidden once the card has been flipped once
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
        document.getElementById('studyDifficultCount').textContent = this.studyStats.difficult;
        
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
            const response = await fetch('/api/v1/revision/api/user-settings/');
            
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
        
        // Store original content for restart
        if (!this.originalStudyAreaContent) {
            this.originalStudyAreaContent = studyArea.innerHTML;
        }
        
        // Create completion message
        studyArea.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-trophy text-warning" style="font-size: 4rem;"></i>
                <h4 class="mt-3">Session terminée !</h4>
                <p class="text-muted">Excellent travail ! Vous avez terminé ${this.studyCards.length} ${window.ngettext('card', 'cards', this.studyCards.length)}.</p>
                <div class="row text-center mt-4 mb-4">
                    <div class="col">
                        <div class="stat-value text-linguify-accent">${this.studyStats.correct}</div>
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
                    <button class="btn btn-outline-custom" id="restartStudyBtn">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Recommencer
                    </button>
                    <button class="btn btn-gradient" id="exitStudyModeBtn">
                        <i class="bi bi-house me-1"></i>
                        Mes decks
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners for the completion buttons
        setTimeout(() => {
            const restartBtn = document.getElementById('restartStudyBtn');
            const exitBtn = document.getElementById('exitStudyModeBtn');
            
            if (restartBtn) {
                restartBtn.addEventListener('click', () => {
                    console.log('Restart button clicked - restarting study');
                    this.restartStudy();
                });
            }
            
            if (exitBtn) {
                exitBtn.addEventListener('click', () => {
                    console.log('Exit to decks list button clicked');
                    this.goToDeckslist();
                });
            }
        }, 100); // Small delay to ensure DOM is updated
    }

    async restartStudy() {
        if (this.currentDeck) {
            console.log('Restarting study for deck:', this.currentDeck.name);
            
            // Restore the original study area content
            const studyArea = document.getElementById('studyArea');
            if (studyArea && this.originalStudyAreaContent) {
                studyArea.innerHTML = this.originalStudyAreaContent;
                studyArea.style.display = 'block';
                
                // Re-attach event listeners that might have been lost
                const flashcard = document.getElementById('flashcard');
                if (flashcard) {
                    // Remove any existing listeners to avoid duplicates
                    flashcard.replaceWith(flashcard.cloneNode(true));
                    const newFlashcard = document.getElementById('flashcard');
                    newFlashcard.addEventListener('click', () => this.flipCard());
                }
                
                // Re-attach difficulty button listeners
                this.reattachDifficultyButtons();
            }
            
            // Restart the study process normally
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
        // Stop any ongoing speech
        this.stopSpeech();
        
        // Hide study mode
        const flashcardElement = document.getElementById('flashcardStudyMode');
        if (flashcardElement) {
            flashcardElement.style.display = 'none';
            flashcardElement.classList.add('study-mode-hidden');
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

    goToDeckslist() {
        // Stop any ongoing speech
        this.stopSpeech();
        
        // Hide study mode
        document.getElementById('flashcardStudyMode').style.display = 'none';
        
        // Clear selected deck and show main decks list
        if (window.revisionMain) {
            window.revisionMain.appState.selectedDeck = null;
            if (window.revisionMain.hideAllSections) {
                window.revisionMain.hideAllSections();
            }
            const elements = window.revisionMain.getElements();
            if (elements.decksList) {
                elements.decksList.style.display = 'block';
            } else if (elements.welcomeState) {
                elements.welcomeState.style.display = 'block';
            }
        }
    }
    
    reattachDifficultyButtons() {
        console.log('Reattaching difficulty button event listeners...');
        
        // Remove existing listeners by cloning the buttons
        const knownBtn = document.getElementById('studyKnown');
        const easyBtn = document.getElementById('studyEasy');  
        const difficultBtn = document.getElementById('studyDifficult');
        
        if (knownBtn) {
            const newKnownBtn = knownBtn.cloneNode(true);
            knownBtn.parentNode.replaceChild(newKnownBtn, knownBtn);
            newKnownBtn.addEventListener('click', () => {
                console.log('Known/Easy button clicked');
                this.markCard('easy');
            });
        }
        
        if (easyBtn) {
            const newEasyBtn = easyBtn.cloneNode(true);
            easyBtn.parentNode.replaceChild(newEasyBtn, easyBtn);
            newEasyBtn.addEventListener('click', () => {
                console.log('Medium button clicked');
                this.markCard('medium');
            });
        }
        
        if (difficultBtn) {
            const newDifficultBtn = difficultBtn.cloneNode(true);
            difficultBtn.parentNode.replaceChild(newDifficultBtn, difficultBtn);
            newDifficultBtn.addEventListener('click', () => {
                console.log('Difficult button clicked');
                this.markCard('difficult');
            });
        }
        
        console.log('Difficulty button event listeners reattached');
    }

    // ===== MÉTHODES POUR LA SYNTHÈSE VOCALE =====
    
    initializeSpeechSynthesis() {
        if (!this.speechSynthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }

        // Configuration par défaut des voix préférées
        this.preferredVoices = {
            'fr-FR': null,
            'en-US': null,
            'es-ES': null,
            'it-IT': null,
            'de-DE': null
        };

        // Paramètres audio par défaut (pourraient venir des settings utilisateur)
        this.audioSettings = {
            enabled: true,
            speed: 0.9,
            pitch: 1.0,
            volume: 1.0,
            autoPlay: false
        };

        // Charger les voix disponibles
        this.loadVoices();
        
        // Les voix peuvent être chargées de manière asynchrone
        this.speechSynthesis.addEventListener('voiceschanged', () => {
            this.loadVoices();
        });

        // Charger les paramètres utilisateur depuis l'API
        this.loadUserAudioSettings();
    }

    loadVoices() {
        this.voices = this.speechSynthesis.getVoices();
        console.log('Voix disponibles:', this.voices.length);
        
        if (this.voices.length > 0) {
            this.categorizeBestVoices();
        }
    }

    async loadUserAudioSettings() {
        // Utiliser les paramètres passés depuis le serveur s'ils sont disponibles
        if (window.userAudioSettings && Object.keys(window.userAudioSettings).length > 0) {
            const settings = window.userAudioSettings;
            console.log('🎵 Utilisation des paramètres audio du serveur:', settings);
            
            // Mettre à jour les paramètres audio
            this.audioSettings = {
                enabled: settings.audio_enabled !== false,
                speed: settings.audio_speed || 0.9,
                pitch: 1.0,
                volume: 1.0,
                autoPlay: settings.auto_play_audio || false
            };

            // Mettre à jour les préférences de genre par langue
            this.preferredGenders = {
                'fr-FR': settings.preferred_gender_french || 'auto',
                'en-US': settings.preferred_gender_english || 'auto',
                'en-GB': settings.preferred_gender_english || 'auto',
                'es-ES': settings.preferred_gender_spanish || 'auto',
                'it-IT': settings.preferred_gender_italian || 'auto',
                'de-DE': settings.preferred_gender_german || 'auto'
            };

            console.log('✅ Paramètres audio chargés depuis le serveur:', this.audioSettings);
            console.log('✅ Préférences de genre chargées depuis le serveur:', this.preferredGenders);
            return;
        }
        
        // Fallback vers l'API si les paramètres serveur ne sont pas disponibles
        try {
            const response = await fetch('/api/v1/revision/api/user-settings/');
            console.log('🔍 API Response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('🔍 API Response data:', data);
                const settings = data.settings || {};
                console.log('🔍 Settings object:', settings);
                
                // Mettre à jour les paramètres audio
                this.audioSettings = {
                    enabled: settings.audio_enabled !== false,
                    speed: settings.audio_speed || 0.9,
                    pitch: 1.0,
                    volume: 1.0,
                    autoPlay: settings.auto_play_audio || false
                };

                // Mettre à jour les préférences de genre par langue depuis l'API
                this.preferredGenders = {
                    'fr-FR': settings.preferred_gender_french || 'auto',
                    'en-US': settings.preferred_gender_english || 'auto',
                    'en-GB': settings.preferred_gender_english || 'auto',
                    'es-ES': settings.preferred_gender_spanish || 'auto',
                    'it-IT': settings.preferred_gender_italian || 'auto',
                    'de-DE': settings.preferred_gender_german || 'auto'
                };

                console.log('✅ Paramètres audio chargés depuis API:', this.audioSettings);
                console.log('✅ Préférences de genre chargées depuis API:', this.preferredGenders);
            } else {
                console.error('❌ API user-settings failed with status:', response.status);
                const errorText = await response.text();
                console.error('❌ Error response:', errorText);
            }
        } catch (error) {
            console.warn('❌ Exception loading user audio settings:', error);
            // Utiliser les paramètres par défaut
        }
    }

    categorizeBestVoices() {
        // Catégoriser les meilleures voix par langue
        const bestVoicesByLanguage = {};
        
        // Critères de qualité pour les voix
        const qualityCriteria = {
            // Préférences par plateforme/navigateur
            preferredEngines: ['neural', 'premium', 'enhanced', 'natural'],
            // Éviter les voix de faible qualité
            avoidKeywords: ['eSpeak', 'Festival', 'robot', 'basic'],
            // Préférer les voix locales
            preferLocal: true
        };

        this.voices.forEach(voice => {
            const langCode = voice.lang;
            const shortLang = langCode.split('-')[0];

            if (!bestVoicesByLanguage[langCode]) {
                bestVoicesByLanguage[langCode] = [];
            }
            
            // Calculer un score de qualité pour cette voix
            let qualityScore = 0;
            
            // Voix locales sont préférées
            if (voice.localService) qualityScore += 10;
            
            // Noms de voix qui indiquent une bonne qualité
            const voiceName = voice.name.toLowerCase();
            qualityCriteria.preferredEngines.forEach(engine => {
                if (voiceName.includes(engine)) qualityScore += 5;
            });
            
            // Pénaliser les voix de mauvaise qualité
            qualityCriteria.avoidKeywords.forEach(keyword => {
                if (voiceName.includes(keyword)) qualityScore -= 10;
            });
            
            // Préférer les voix avec des noms spécifiques par langue
            if (shortLang === 'en' && (voiceName.includes('samantha') || voiceName.includes('alex') || voiceName.includes('karen'))) {
                qualityScore += 3;
            } else if (shortLang === 'fr' && (voiceName.includes('amelie') || voiceName.includes('thomas') || voiceName.includes('marie'))) {
                qualityScore += 3;
            }
            
            voice.qualityScore = qualityScore;
            bestVoicesByLanguage[langCode].push(voice);
        });

        // Trier les voix par score de qualité
        Object.keys(bestVoicesByLanguage).forEach(lang => {
            bestVoicesByLanguage[lang].sort((a, b) => b.qualityScore - a.qualityScore);
        });

        this.bestVoicesByLanguage = bestVoicesByLanguage;
        
        console.log('Meilleures voix par langue:', bestVoicesByLanguage);
    }

    detectLanguage(text) {
        // Détection simple de la langue basée sur des caractères et mots communs
        if (!text) return 'fr-FR';
        
        const textLower = text.toLowerCase();
        
        // Français - mots communs et accents
        const frenchPatterns = [
            /[àâäçéèêëïîôöùûüÿ]/,
            /\b(le|la|les|un|une|des|de|du|et|est|être|avoir|que|qui|dans|pour|avec|sur|par|ce|cette|tout|tous|toute|mais|ou|où|comme|très|plus|sans|sous|entre|pendant|après|avant|depuis|jusqu|alors|ainsi|donc|car|si|bien|encore|aussi|même|déjà|ici|là|maintenant|hier|demain|aujourd|bonjour|bonsoir|merci|salut|comment|pourquoi|quand|combien|beaucoup|peu|jamais|toujours|souvent|parfois|peut|peuvent|doit|peuvent|faire|dire|aller|venir|voir|savoir|vouloir|pouvoir)\b/
        ];
        
        // Anglais - mots communs
        const englishPatterns = [
            /\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by|from|up|about|into|over|after|beneath|under|above|through|during|before|since|until|while|although|because|if|when|where|what|who|which|how|why|that|this|these|those|some|any|many|much|few|little|all|both|each|every|other|another|such|same|different|new|old|first|last|next|good|bad|big|small|long|short|high|low|hot|cold|fast|slow|easy|hard|right|wrong|true|false|yes|no|hello|hi|goodbye|bye|please|thank|thanks|sorry|excuse|welcome)\b/
        ];
        
        // Espagnol - mots communs et accents
        const spanishPatterns = [
            /[áéíóúñü]/,
            /\b(el|la|los|las|un|una|unos|unas|de|del|y|o|pero|en|por|para|con|sin|sobre|bajo|entre|durante|después|antes|desde|hasta|mientras|aunque|porque|si|cuando|donde|que|quien|como|por|qué|cuándo|dónde|cuánto|mucho|poco|nunca|siempre|a|menudo|vez|veces|puede|pueden|debe|deben|hacer|decir|ir|venir|ver|saber|querer|poder|ser|estar|tener|haber|hola|adiós|gracias|por|favor|lo|siento|perdón|bienvenido)\b/
        ];
        
        // Italien - mots communs et accents
        const italianPatterns = [
            /[àèéìíîòóù]/,
            /\b(il|la|lo|gli|le|un|una|uno|di|del|della|dei|delle|e|o|ma|in|su|per|con|senza|sopra|sotto|tra|fra|durante|dopo|prima|da|fino|mentre|anche|se|perché|quando|dove|che|chi|come|quanto|molto|poco|mai|sempre|spesso|volte|può|possono|deve|devono|fare|dire|andare|venire|vedere|sapere|volere|potere|essere|avere|ciao|arrivederci|grazie|prego|scusi|benvenuto)\b/
        ];
        
        // Allemand - mots communs et caractères
        const germanPatterns = [
            /[äöüß]/,
            /\b(der|die|das|den|dem|des|ein|eine|eines|einem|einer|und|oder|aber|in|an|auf|für|mit|ohne|über|unter|zwischen|während|nach|vor|von|bis|während|obwohl|weil|wenn|wo|was|wer|wie|warum|wann|viel|wenig|nie|immer|oft|manchmal|kann|können|muss|müssen|soll|sollen|machen|sagen|gehen|kommen|sehen|wissen|wollen|können|sein|haben|hallo|auf|wiedersehen|danke|bitte|entschuldigung|willkommen)\b/
        ];

        // Compter les correspondances pour chaque langue
        let frenchScore = 0;
        let englishScore = 0;
        let spanishScore = 0;
        let italianScore = 0;
        let germanScore = 0;

        frenchPatterns.forEach(pattern => {
            const matches = textLower.match(pattern);
            if (matches) frenchScore += matches.length;
        });

        englishPatterns.forEach(pattern => {
            const matches = textLower.match(pattern);
            if (matches) englishScore += matches.length;
        });

        spanishPatterns.forEach(pattern => {
            const matches = textLower.match(pattern);
            if (matches) spanishScore += matches.length;
        });

        italianPatterns.forEach(pattern => {
            const matches = textLower.match(pattern);
            if (matches) italianScore += matches.length;
        });

        germanPatterns.forEach(pattern => {
            const matches = textLower.match(pattern);
            if (matches) germanScore += matches.length;
        });

        // Déterminer la langue avec le score le plus élevé
        const scores = [
            { lang: 'fr-FR', score: frenchScore },
            { lang: 'en-US', score: englishScore },
            { lang: 'es-ES', score: spanishScore },
            { lang: 'it-IT', score: italianScore },
            { lang: 'de-DE', score: germanScore }
        ];

        scores.sort((a, b) => b.score - a.score);
        
        // Si aucun pattern n'est détecté, retourner français par défaut
        return scores[0].score > 0 ? scores[0].lang : 'fr-FR';
    }

    normalizeLanguageCode(langCode) {
        if (!langCode) return null;
        
        const langMap = {
            'fr': 'fr-FR',
            'en': 'en-US', 
            'es': 'es-ES',
            'it': 'it-IT',
            'de': 'de-DE',
            'pt': 'pt-PT',
            'ru': 'ru-RU',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN'
        };
        
        const normalized = langCode.toLowerCase().trim();
        return langMap[normalized] || langCode;
    }

    getBestVoiceForLanguage(languageCode, preferredGender = null) {
        if (!this.voices.length) {
            this.loadVoices();
        }

        // 1. Déterminer le genre préféré pour cette langue
        let targetGender = preferredGender;
        if (!targetGender && this.preferredGenders && this.preferredGenders[languageCode]) {
            targetGender = this.preferredGenders[languageCode];
        }
        
        console.log(`🔍 Recherche voix pour ${languageCode} avec genre préféré: ${targetGender || 'auto'}`);

        // 2. Si un genre spécifique est demandé, chercher les meilleures voix de ce genre
        if (targetGender && targetGender !== 'auto') {
            const voicesForLanguage = this.voices.filter(v => v.lang === languageCode || v.lang.startsWith(languageCode.split('-')[0]));
            const voicesByGender = this.categorizeVoicesByGender(voicesForLanguage);
            
            const targetVoices = voicesByGender[targetGender] || [];
            if (targetVoices.length > 0) {
                // Prendre la meilleure voix de ce genre (score qualité le plus élevé)
                const bestVoice = targetVoices.sort((a, b) => (b.qualityScore || 0) - (a.qualityScore || 0))[0];
                console.log(`✅ Voix ${targetGender} sélectionnée automatiquement: ${bestVoice.name} (score: ${bestVoice.qualityScore || 'N/A'})`);
                return bestVoice;
            } else {
                console.warn(`❌ Aucune voix ${targetGender} trouvée pour ${languageCode}, utilisation du fallback automatique`);
            }
        }

        // 2. Utiliser nos voix classées par qualité
        if (this.bestVoicesByLanguage && this.bestVoicesByLanguage[languageCode]) {
            const bestVoices = this.bestVoicesByLanguage[languageCode];
            if (bestVoices.length > 0) {
                console.log(`Utilisation de la meilleure voix pour ${languageCode}: ${bestVoices[0].name} (score: ${bestVoices[0].qualityScore})`);
                return bestVoices[0];
            }
        }

        // 3. Fallback : essayer de trouver une voix pour la langue exacte
        let voice = this.voices.find(v => v.lang === languageCode);
        
        // 4. Si pas trouvé, essayer avec juste le code de langue (ex: 'fr' au lieu de 'fr-FR')
        if (!voice) {
            const shortLang = languageCode.split('-')[0];
            const languageVoices = this.voices.filter(v => v.lang.startsWith(shortLang));
            
            if (languageVoices.length > 0) {
                // Préférer les voix locales
                const localVoices = languageVoices.filter(v => v.localService);
                voice = localVoices.length > 0 ? localVoices[0] : languageVoices[0];
            }
        }
        
        // 5. Si toujours pas trouvé, prendre une voix par défaut
        if (!voice && this.voices.length > 0) {
            voice = this.voices[0];
        }
        
        return voice;
    }

    // Nouvelle méthode pour obtenir la liste des voix disponibles pour une langue (pour les settings)
    getAvailableVoicesForLanguage(languageCode) {
        const shortLang = languageCode.split('-')[0];
        return this.voices
            .filter(v => v.lang.startsWith(shortLang))
            .map(v => ({
                name: v.name,
                lang: v.lang,
                localService: v.localService,
                qualityScore: v.qualityScore || 0
            }))
            .sort((a, b) => (b.qualityScore || 0) - (a.qualityScore || 0));
    }

    categorizeVoicesByGender(voices) {
        const genderPatterns = {
            male: [
                // Noms masculins courants
                'paul', 'george', 'david', 'mark', 'richard', 'daniel', 'thomas', 'matthew', 'james', 'john',
                'pierre', 'jean', 'michel', 'henri', 'louis', 'françois', 'antoine', 'nicolas',
                'carlos', 'diego', 'antonio', 'fernando', 'miguel', 'josé', 'manuel', 'francisco',
                'marco', 'giovanni', 'francesco', 'andrea', 'alessandro', 'lorenzo', 'matteo',
                'klaus', 'hans', 'wolfgang', 'stefan', 'michael', 'andreas', 'christian',
                // Noms masculins anglais plus spécifiques
                'william', 'robert', 'charles', 'christopher', 'anthony', 'brian', 'kevin', 'edward',
                'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob', 'gary', 'nicholas', 'eric',
                'jonathan', 'stephen', 'larry', 'justin', 'scott', 'brandon', 'benjamin', 'samuel',
                'gregory', 'alexander', 'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron',
                // Indicateurs explicites (priorité haute pour l'anglais)
                'male', 'man', 'masculin', 'homme', 'hombre', 'uomo', 'mann'
            ],
            female: [
                // Noms féminins courants
                'julie', 'marie', 'sarah', 'emma', 'sophie', 'claire', 'anne', 'lisa', 'susan', 'helen',
                'amélie', 'isabelle', 'nathalie', 'véronique', 'christine', 'françoise', 'martine',
                'maria', 'carmen', 'ana', 'lucia', 'pilar', 'rosa', 'elena', 'patricia',
                'giulia', 'francesca', 'elena', 'sara', 'anna', 'valentina', 'chiara',
                'anna', 'maria', 'petra', 'sabine', 'christine', 'angelika', 'barbara',
                // Indicateurs explicites
                'female', 'woman', 'féminin', 'femme', 'mujer', 'donna', 'frau'
            ]
        };

        // Voix anglaises masculines de haute qualité (patterns étendus pour une meilleure détection)
        const premiumEnglishMaleVoices = [
            'microsoft david', 'google uk english male', 'microsoft ryan', 'microsoft frank',
            'google us english male', 'microsoft sean', 'google australian male', 'microsoft kevin',
            'alex', 'daniel', 'samantha male', 'tom', 'nathan', 'aaron enhanced', 'fred',
            // Ajout de patterns plus larges pour détecter les voix système
            'male', 'man', 'masculine', 'guy', 'boy', 'mr', 'sir'
        ];

        // Voix anglaises féminines de haute qualité
        const premiumEnglishFemaleVoices = [
            'microsoft zira', 'microsoft eva', 'google uk english female', 'microsoft hazel',
            'google us english female', 'microsoft aria', 'google australian female', 'microsoft natasha',
            'samantha', 'victoria', 'kate', 'alice', 'emma', 'olivia', 'sophia',
            // Ajout de patterns plus larges pour détecter les voix système
            'female', 'woman', 'feminine', 'girl', 'lady', 'ms', 'mrs'
        ];

        const result = { male: [], female: [], unknown: [] };

        for (const voice of voices) {
            const voiceName = voice.name.toLowerCase();
            let gender = 'unknown';
            let qualityBonus = 0;

            // DÉTECTION PRÉCISE PAR MOT-CLÉ EXPLICITE (priorité absolue)
            if (voice.lang && voice.lang.startsWith('en')) {
                // D'abord vérifier les mots-clés explicites de genre
                if (voiceName.includes('female') || voiceName.includes('woman') || voiceName.includes('feminine')) {
                    gender = 'female';
                    qualityBonus = 100;
                    console.log(`👩 Voix féminine détectée par mot-clé explicite: ${voice.name} (bonus: ${qualityBonus})`);
                } else if (voiceName.includes('male') || voiceName.includes('man') || voiceName.includes('masculine')) {
                    gender = 'male';  
                    qualityBonus = 100;
                    console.log(`👨 Voix masculine détectée par mot-clé explicite: ${voice.name} (bonus: ${qualityBonus})`);
                }
                
                // Si pas encore déterminé, vérifier les voix féminines premium spécifiques
                if (gender === 'unknown') {
                    for (let i = 0; i < premiumEnglishFemaleVoices.length; i++) {
                        if (voiceName.includes(premiumEnglishFemaleVoices[i]) && !voiceName.includes('male')) {
                            gender = 'female';
                            qualityBonus = 50 + (premiumEnglishFemaleVoices.length - i) * 10;
                            console.log(`🎯 Voix anglaise féminine premium détectée: ${voice.name} (bonus: ${qualityBonus})`);
                            break;
                        }
                    }
                }
                
                // Si pas encore déterminé, vérifier les voix masculines premium spécifiques
                if (gender === 'unknown') {
                    for (let i = 0; i < premiumEnglishMaleVoices.length; i++) {
                        if (voiceName.includes(premiumEnglishMaleVoices[i]) && !voiceName.includes('female')) {
                            gender = 'male';
                            qualityBonus = 50 + (premiumEnglishMaleVoices.length - i) * 10;
                            console.log(`🎯 Voix anglaise masculine premium détectée: ${voice.name} (bonus: ${qualityBonus})`);
                            break;
                        }
                    }
                }
            }

            // Si pas encore identifié, vérifier les patterns masculins standards
            if (gender === 'unknown') {
                for (const pattern of genderPatterns.male) {
                    if (voiceName.includes(pattern)) {
                        gender = 'male';
                        // Bonus supplémentaire pour les voix anglaises masculines
                        if (voice.lang && voice.lang.startsWith('en')) {
                            qualityBonus = 20;
                        }
                        break;
                    }
                }
            }

            // Si pas trouvé masculin, vérifier les patterns féminins
            if (gender === 'unknown') {
                for (const pattern of genderPatterns.female) {
                    if (voiceName.includes(pattern)) {
                        gender = 'female';
                        // Bonus supplémentaire pour les voix anglaises féminines
                        if (voice.lang && voice.lang.startsWith('en')) {
                            qualityBonus = 20;
                        }
                        break;
                    }
                }
            }

            // Appliquer le bonus qualité
            if (qualityBonus > 0) {
                voice.qualityScore = (voice.qualityScore || 0) + qualityBonus;
            }

            result[gender].push(voice);
        }

        // Trier les voix masculines par score de qualité pour chaque langue
        result.male.sort((a, b) => {
            // Prioriser d'abord les voix anglaises avec bonus
            if (a.lang && a.lang.startsWith('en') && (!b.lang || !b.lang.startsWith('en'))) {
                return -1;
            }
            if (b.lang && b.lang.startsWith('en') && (!a.lang || !a.lang.startsWith('en'))) {
                return 1;
            }
            // Puis trier par score de qualité
            return (b.qualityScore || 0) - (a.qualityScore || 0);
        });

        // Trier aussi les voix féminines par score de qualité
        result.female.sort((a, b) => {
            // Prioriser d'abord les voix anglaises avec bonus
            if (a.lang && a.lang.startsWith('en') && (!b.lang || !b.lang.startsWith('en'))) {
                return -1;
            }
            if (b.lang && b.lang.startsWith('en') && (!a.lang || !a.lang.startsWith('en'))) {
                return 1;
            }
            // Puis trier par score de qualité
            return (b.qualityScore || 0) - (a.qualityScore || 0);
        });

        // Debug: Afficher les résultats de la catégorisation pour l'anglais
        const englishVoices = voices.filter(v => v.lang && v.lang.startsWith('en'));
        if (englishVoices.length > 0) {
            console.log('🔍 Catégorisation des voix anglaises:');
            console.log(`📊 Masculines (${result.male.filter(v => v.lang.startsWith('en')).length}):`, 
                result.male.filter(v => v.lang.startsWith('en')).map(v => `${v.name} (score: ${v.qualityScore || 0})`));
            console.log(`📊 Féminines (${result.female.filter(v => v.lang.startsWith('en')).length}):`, 
                result.female.filter(v => v.lang.startsWith('en')).map(v => `${v.name} (score: ${v.qualityScore || 0})`));
            console.log(`📊 Inconnues (${result.unknown.filter(v => v.lang.startsWith('en')).length}):`, 
                result.unknown.filter(v => v.lang.startsWith('en')).map(v => v.name));
        }

        return result;
    }

    speakText(side) {
        if (!this.speechSynthesis || !this.audioSettings.enabled) {
            console.warn('Speech synthesis not supported or disabled');
            return;
        }

        // Arrêter toute lecture en cours
        this.stopSpeech();

        const currentCard = this.studyCards[this.currentCardIndex];
        if (!currentCard) return;

        let textToSpeak = '';
        let buttonElement = null;
        let cardLanguage = null;
        
        if (side === 'front') {
            textToSpeak = currentCard.front_text;
            buttonElement = document.getElementById('speakFrontBtn');
            cardLanguage = currentCard.front_language;
        } else if (side === 'back') {
            textToSpeak = currentCard.back_text;
            buttonElement = document.getElementById('speakBackBtn');
            cardLanguage = currentCard.back_language;
        }

        if (!textToSpeak || !textToSpeak.trim()) {
            console.warn('No text to speak');
            return;
        }

        // Nettoyer le texte pour la synthèse vocale
        textToSpeak = this.cleanTextForSpeech(textToSpeak);

        // Utiliser la langue définie dans la carte, sinon détecter automatiquement
        let languageToUse;
        if (cardLanguage && cardLanguage.trim()) {
            // La carte a une langue définie
            languageToUse = this.normalizeLanguageCode(cardLanguage);
            console.log(`Texte: "${textToSpeak}" - Langue définie: ${cardLanguage} -> ${languageToUse}`);
        } else {
            // Fallback sur la détection automatique
            languageToUse = this.detectLanguage(textToSpeak);
            console.log(`Texte: "${textToSpeak}" - Langue détectée automatiquement: ${languageToUse}`);
        }

        // Créer l'utterance
        this.currentUtterance = new SpeechSynthesisUtterance(textToSpeak);
        
        // Configurer la voix selon les préférences utilisateur
        const voice = this.getBestVoiceForLanguage(languageToUse);
        if (voice) {
            this.currentUtterance.voice = voice;
            this.currentUtterance.lang = voice.lang;
            console.log(`Voix utilisée: ${voice.name} (${voice.lang}) - Score qualité: ${voice.qualityScore || 'N/A'}`);
        } else {
            this.currentUtterance.lang = languageToUse;
            console.log(`Pas de voix trouvée, utilisation de la langue: ${languageToUse}`);
        }

        // Utiliser les paramètres utilisateur pour la configuration
        this.currentUtterance.rate = this.audioSettings.speed;
        this.currentUtterance.pitch = this.audioSettings.pitch;
        this.currentUtterance.volume = this.audioSettings.volume;

        // Animation du bouton pendant la lecture
        if (buttonElement) {
            buttonElement.classList.add('speaking');
        }

        // Gérer les événements
        this.currentUtterance.onstart = () => {
            console.log('Début de la lecture');
        };

        this.currentUtterance.onend = () => {
            console.log('Fin de la lecture');
            if (buttonElement) {
                buttonElement.classList.remove('speaking');
            }
            this.currentUtterance = null;
        };

        this.currentUtterance.onerror = (event) => {
            console.error('Erreur lors de la lecture:', event.error);
            if (buttonElement) {
                buttonElement.classList.remove('speaking');
            }
            this.currentUtterance = null;
        };

        // Lancer la lecture
        this.speechSynthesis.speak(this.currentUtterance);
    }

    stopSpeech() {
        if (this.speechSynthesis && this.speechSynthesis.speaking) {
            this.speechSynthesis.cancel();
        }
        
        // Nettoyer l'animation des boutons
        const frontBtn = document.getElementById('speakFrontBtn');
        const backBtn = document.getElementById('speakBackBtn');
        
        if (frontBtn) frontBtn.classList.remove('speaking');
        if (backBtn) backBtn.classList.remove('speaking');
        
        this.currentUtterance = null;
    }

    cleanTextForSpeech(text) {
        if (!text) return text;
        
        // Nettoyage du texte pour améliorer la prononciation
        let cleanedText = text;
        
        // Remplacer les barres obliques par des pauses
        cleanedText = cleanedText.replace(/\s*\/\s*/g, ' ... '); // "/" devient " ... "
        
        // Remplacer d'autres caractères problématiques
        cleanedText = cleanedText.replace(/\s*\|\s*/g, ' ... '); // "|" devient " ... "
        cleanedText = cleanedText.replace(/\s*-\s*/g, ' ... ');   // "-" isolé devient " ... "
        
        // Nettoyer les parenthèses (optionnel - les garder ou les supprimer selon préférence)
        // cleanedText = cleanedText.replace(/\([^)]*\)/g, ''); // Supprimer le contenu entre parenthèses
        
        // Nettoyer les crochets
        cleanedText = cleanedText.replace(/\[[^\]]*\]/g, ''); // Supprimer le contenu entre crochets
        
        // Remplacer les symboles mathématiques par des mots
        cleanedText = cleanedText.replace(/\+/g, ' plus ');
        cleanedText = cleanedText.replace(/=/g, ' égale ');
        cleanedText = cleanedText.replace(/</g, ' inférieur à ');
        cleanedText = cleanedText.replace(/>/g, ' supérieur à ');
        
        // Nettoyer les espaces multiples
        cleanedText = cleanedText.replace(/\s+/g, ' ').trim();
        
        console.log(`Text cleaning: "${text}" → "${cleanedText}"`);
        
        return cleanedText;
    }

    // ===== MÉTHODES UTILITAIRES POUR DÉBUGGAGE ET CONFIGURATION =====
    
    // Méthode pour tester les voix disponibles (appelable depuis la console)
    testVoicesForLanguage(languageCode = 'en-US') {
        const availableVoices = this.getAvailableVoicesForLanguage(languageCode);
        console.log(`Voix disponibles pour ${languageCode}:`, availableVoices);
        
        availableVoices.forEach((voiceInfo, index) => {
            console.log(`${index + 1}. ${voiceInfo.name} (${voiceInfo.lang}) - Score: ${voiceInfo.qualityScore} - Local: ${voiceInfo.localService}`);
        });
        
        return availableVoices;
    }
    
    // Méthode pour tester une voix spécifique
    testVoice(voiceName, text = 'Hello, this is a test') {
        const voice = this.voices.find(v => v.name === voiceName);
        if (!voice) {
            console.error(`Voix "${voiceName}" non trouvée`);
            return false;
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = voice;
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        utterance.onstart = () => console.log(`Test de la voix: ${voice.name}`);
        utterance.onend = () => console.log(`Test terminé: ${voice.name}`);
        
        this.speechSynthesis.speak(utterance);
        return true;
    }
    
    // Méthode pour définir une voix préférée
    setPreferredVoice(languageCode, voiceName) {
        const voice = this.voices.find(v => v.name === voiceName);
        if (!voice) {
            console.error(`Voix "${voiceName}" non trouvée`);
            return false;
        }
        
        this.preferredVoices[languageCode] = voiceName;
        console.log(`Voix préférée définie pour ${languageCode}: ${voiceName}`);
        
        // TODO: Sauvegarder dans les paramètres utilisateur
        return true;
    }

    // Méthode pour lister toutes les voix par langue
    listAllVoicesByLanguage() {
        const voicesByLang = {};
        this.voices.forEach(voice => {
            const shortLang = voice.lang.split('-')[0];
            if (!voicesByLang[shortLang]) {
                voicesByLang[shortLang] = [];
            }
            voicesByLang[shortLang].push({
                name: voice.name,
                lang: voice.lang,
                localService: voice.localService,
                qualityScore: voice.qualityScore || 0
            });
        });
        
        console.log('Toutes les voix par langue:', voicesByLang);
        return voicesByLang;
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
    console.log('🔄 Initializing FlashcardStudyMode...');
    try {
        window.flashcardMode = new FlashcardStudyMode();
        console.log('✅ FlashcardStudyMode initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing FlashcardStudyMode:', error);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlashcardStudyMode;
}