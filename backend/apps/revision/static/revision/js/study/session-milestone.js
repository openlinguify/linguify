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
        this.milestoneInterval = 7; // Afficher un jalon tous les 7 cartes
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

                // Vérifier si on doit afficher un jalon au démarrage
                if (data.should_show_milestone) {
                    this.showMilestone(data);
                }
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

                // Vérifier si on doit afficher un jalon
                if (data.should_show_milestone) {
                    await this.showMilestone(data);
                    // Marquer le jalon comme affiché
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
     * Affiche le modal de jalon
     */
    showMilestone(sessionData) {
        const {
            progress_percentage = 0,
            cards_completed = 0,
            cards_until_next_milestone = 0,
            accuracy_rate = null
        } = sessionData;

        // Messages motivants selon la progression
        let title = "Heureux de vous revoir !";
        let subtitle = "Prêt à bosser dur aujourd'hui ?";

        if (progress_percentage > 0) {
            if (progress_percentage >= 75) {
                title = "Excellent progrès ! 🎉";
                subtitle = "Vous êtes presque au bout !";
            } else if (progress_percentage >= 50) {
                title = "À mi-chemin ! 💪";
                subtitle = "Continue comme ça !";
            } else if (progress_percentage >= 25) {
                title = "Bon début ! 👍";
                subtitle = "Gardez le rythme !";
            } else {
                title = "C'est parti ! 🚀";
                subtitle = "Un pas à la fois !";
            }
        }

        // Afficher le modal via le composant global
        if (window.milestoneModal) {
            window.milestoneModal.show({
                title,
                subtitle,
                progressPercent: progress_percentage,
                completed: cards_completed,
                remaining: cards_until_next_milestone,
                accuracy: accuracy_rate,
                showRestart: progress_percentage > 0
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
