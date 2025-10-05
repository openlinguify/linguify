/**
 * Session Milestone Manager
 * Gère les jalons (milestones) dans les sessions d'étude
 */

class SessionMilestoneManager {
    constructor() {
        this.sessionId = null;
        this.totalCards = 0;
        this.cardsCompleted = 0;
        this.cardsCorrect = 0;
        this.milestoneInterval = 10; // Afficher un jalon tous les 10 cartes minimum
        this.lastMilestoneShown = 0;
        this.sessionStartTime = null;
        this.hasShownWelcome = false; // Pour afficher un message de bienvenue une seule fois
    }

    /**
     * Initialise ou récupère une session
     */
    async initSession(deckId, studyMode = 'flashcards') {
        try {
            const response = await fetch('/revision/api/session/milestone/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    deck_id: deckId,
                    study_mode: studyMode
                })
            });

            if (!response.ok) {
                throw new Error('Failed to initialize session');
            }

            const data = await response.json();

            if (data.success) {
                this.sessionId = data.session_id;
                this.totalCards = data.total_cards;
                this.cardsCompleted = data.cards_completed;
                this.cardsCorrect = data.cards_correct;
                this.sessionStartTime = Date.now();

                // Ne PAS afficher de modal au démarrage - c'est agaçant
                // L'utilisateur veut juste commencer à étudier
            }

            return data;
        } catch (error) {
            console.error('Error initializing session:', error);
            return null;
        }
    }

    /**
     * Enregistre une tentative de carte
     */
    async recordCardAttempt(isCorrect) {
        if (!this.sessionId) {
            console.warn('No active session');
            return null;
        }

        try {
            const response = await fetch(`/revision/api/session/milestone/${this.sessionId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    is_correct: isCorrect
                })
            });

            if (!response.ok) {
                throw new Error('Failed to record card attempt');
            }

            const data = await response.json();

            if (data.success) {
                this.cardsCompleted = data.cards_completed;
                this.cardsCorrect = data.cards_correct;

                // Logique intelligente pour afficher le modal
                if (this.shouldShowMilestone(data)) {
                    await this.showMilestone(data);
                    this.lastMilestoneShown = this.cardsCompleted;
                    await this.markMilestoneShown();
                }
            }

            return data;
        } catch (error) {
            console.error('Error recording card attempt:', error);
            return null;
        }
    }

    /**
     * Détermine intelligemment si on doit afficher un milestone
     */
    shouldShowMilestone(data) {
        const progress = data.progress_percentage || 0;
        const cardsCompleted = data.cards_completed || 0;
        const cardsSinceLastMilestone = cardsCompleted - this.lastMilestoneShown;

        // Ne jamais afficher si moins de 10 cartes depuis le dernier milestone
        if (cardsSinceLastMilestone < this.milestoneInterval) {
            return false;
        }

        // Afficher aux moments clés :
        // - 25% (premier quart)
        // - 50% (mi-parcours)
        // - 75% (presque fini)
        // - 100% (terminé - mais géré par l'écran de fin)
        const isKeyMilestone = progress === 25 || progress === 50 || progress === 75;

        // OU afficher tous les 20 cartes pour les longues sessions
        const isLongSessionMilestone = cardsSinceLastMilestone >= 20;

        return isKeyMilestone || isLongSessionMilestone;
    }

    /**
     * Affiche le modal de jalon
     */
    showMilestone(sessionData) {
        const {
            progress_percentage = 0,
            cards_completed = 0,
            cards_until_next_milestone = 0,
            accuracy_rate = null
        } = sessionData;

        const accuracyPercent = accuracy_rate ? Math.round(accuracy_rate * 100) : 0;
        const totalCards = this.totalCards;
        const remaining = totalCards - cards_completed;

        // Messages intelligents et utiles selon la progression ET la performance
        let title = "";
        let subtitle = "";

        // Messages basés sur les jalons clés
        if (progress_percentage === 25) {
            title = "Premier quart terminé ! 🎯";
            subtitle = accuracyPercent >= 80
                ? `Excellent début : ${accuracyPercent}% de réussite !`
                : `Continuez à vous concentrer. ${remaining} cartes restantes.`;
        } else if (progress_percentage === 50) {
            title = "Mi-parcours ! 💪";
            subtitle = accuracyPercent >= 80
                ? `Superbe performance : ${accuracyPercent}% de bonnes réponses !`
                : `Plus que ${remaining} cartes. Vous pouvez le faire !`;
        } else if (progress_percentage === 75) {
            title = "Dernière ligne droite ! 🏁";
            subtitle = accuracyPercent >= 80
                ? `Bravo ! ${accuracyPercent}% de réussite, continuez !`
                : `Plus que ${remaining} cartes avant la fin !`;
        } else {
            // Pour les longues sessions (tous les 20 cartes)
            const sessionMinutes = this.sessionStartTime
                ? Math.floor((Date.now() - this.sessionStartTime) / 60000)
                : 0;

            title = `${cards_completed} cartes étudiées 📚`;
            subtitle = sessionMinutes > 0
                ? `${sessionMinutes} min d'étude · ${accuracyPercent}% de réussite`
                : `Taux de réussite : ${accuracyPercent}%`;
        }

        // Afficher le modal via le composant global
        if (window.milestoneModal) {
            window.milestoneModal.show({
                title,
                subtitle,
                progressPercent: progress_percentage,
                completed: cards_completed,
                remaining: remaining,
                accuracy: accuracyPercent,
                showRestart: false // Ne pas proposer de redémarrer en pleine session
            });
        }
    }

    /**
     * Marque le jalon comme affiché
     */
    async markMilestoneShown() {
        if (!this.sessionId) return;

        try {
            const response = await fetch(`/revision/api/session/milestone/${this.sessionId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Failed to mark milestone as shown');
            }

            return await response.json();
        } catch (error) {
            console.error('Error marking milestone:', error);
            return null;
        }
    }

    /**
     * Calcule le pourcentage de progression
     */
    getProgressPercentage() {
        if (this.totalCards === 0) return 0;
        return Math.round((this.cardsCompleted / this.totalCards) * 100);
    }

    /**
     * Calcule le taux de réussite
     */
    getAccuracyRate() {
        if (this.cardsCompleted === 0) return 0;
        return Math.round((this.cardsCorrect / this.cardsCompleted) * 100);
    }

    /**
     * Réinitialise la session
     */
    reset() {
        this.sessionId = null;
        this.totalCards = 0;
        this.cardsCompleted = 0;
        this.cardsCorrect = 0;
    }
}

// Exporter pour utilisation globale
window.SessionMilestoneManager = SessionMilestoneManager;
