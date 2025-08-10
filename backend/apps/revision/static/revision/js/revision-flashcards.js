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

        // Stop any ongoing speech when loading a new card
        this.stopSpeech();

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
        // Stop any ongoing speech
        this.stopSpeech();
        
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

    // ===== MÉTHODES POUR LA SYNTHÈSE VOCALE =====
    
    initializeSpeechSynthesis() {
        if (!this.speechSynthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }

        // Charger les voix disponibles
        this.loadVoices();
        
        // Les voix peuvent être chargées de manière asynchrone
        this.speechSynthesis.addEventListener('voiceschanged', () => {
            this.loadVoices();
        });
    }

    loadVoices() {
        this.voices = this.speechSynthesis.getVoices();
        console.log('Voix disponibles:', this.voices.length);
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

    getBestVoiceForLanguage(languageCode) {
        if (!this.voices.length) {
            this.loadVoices();
        }

        // Essayer de trouver une voix pour la langue exacte
        let voice = this.voices.find(v => v.lang === languageCode);
        
        // Si pas trouvé, essayer avec juste le code de langue (ex: 'fr' au lieu de 'fr-FR')
        if (!voice) {
            const shortLang = languageCode.split('-')[0];
            voice = this.voices.find(v => v.lang.startsWith(shortLang));
        }
        
        // Si toujours pas trouvé, prendre une voix par défaut
        if (!voice && this.voices.length > 0) {
            voice = this.voices[0];
        }
        
        return voice;
    }

    speakText(side) {
        if (!this.speechSynthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }

        // Arrêter toute lecture en cours
        this.stopSpeech();

        const currentCard = this.studyCards[this.currentCardIndex];
        if (!currentCard) return;

        let textToSpeak = '';
        let buttonElement = null;
        
        if (side === 'front') {
            textToSpeak = currentCard.front_text;
            buttonElement = document.getElementById('speakFrontBtn');
        } else if (side === 'back') {
            textToSpeak = currentCard.back_text;
            buttonElement = document.getElementById('speakBackBtn');
        }

        if (!textToSpeak || !textToSpeak.trim()) {
            console.warn('No text to speak');
            return;
        }

        // Détecter la langue du texte
        const detectedLanguage = this.detectLanguage(textToSpeak);
        console.log(`Texte: "${textToSpeak}" - Langue détectée: ${detectedLanguage}`);

        // Créer l'utterance
        this.currentUtterance = new SpeechSynthesisUtterance(textToSpeak);
        
        // Configurer la voix
        const voice = this.getBestVoiceForLanguage(detectedLanguage);
        if (voice) {
            this.currentUtterance.voice = voice;
            this.currentUtterance.lang = voice.lang;
            console.log(`Voix utilisée: ${voice.name} (${voice.lang})`);
        } else {
            this.currentUtterance.lang = detectedLanguage;
            console.log(`Pas de voix trouvée, utilisation de la langue: ${detectedLanguage}`);
        }

        // Configurer les paramètres
        this.currentUtterance.rate = 0.9; // Vitesse légèrement plus lente
        this.currentUtterance.pitch = 1.0;
        this.currentUtterance.volume = 1.0;

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