// apps/revision/static/src/js/components/RevisionStudyModes.js

const { Component } = owl;

/**
 * Composant pour afficher les différents modes d'étude de révision
 * Migré depuis frontend flashcard components
 */
export class RevisionStudyModes extends Component {
    static template = "RevisionStudyModes";
    static props = {
        deckId: Number,
        deckStats: { type: Object, optional: true },
        onModeSelect: Function
    };

    setup() {
        this.studyModes = [
            {
                id: 'flashcards',
                name: 'Flashcards',
                description: 'Révisez vos cartes une par une avec la possibilité de les retourner',
                icon: '🃏',
                path: 'flashcards',
                minCards: 1,
                recommended: true
            },
            {
                id: 'learn',
                name: 'Apprendre',
                description: 'Mode d\'apprentissage adaptatif avec questions à choix multiples',
                icon: '🎓',
                path: 'learn',
                minCards: 4,
                recommended: false
            },
            {
                id: 'match',
                name: 'Association',
                description: 'Associez les termes avec leurs définitions dans un jeu de mémoire',
                icon: '🧩',
                path: 'match',
                minCards: 6,
                recommended: false
            },
            {
                id: 'review',
                name: 'Révision',
                description: 'Révisez rapidement les cartes que vous devez revoir',
                icon: '📝',
                path: 'review',
                minCards: 1,
                recommended: false
            }
        ];
    }

    // === GESTION DES ACTIONS ===

    onSelectMode(mode) {
        if (!this.isModeAvailable(mode)) return;
        
        this.props.onModeSelect(mode.id, {
            deckId: this.props.deckId,
            path: mode.path
        });
    }

    // === HELPERS ===

    isModeAvailable(mode) {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        
        // Cas spécial pour le mode révision
        if (mode.id === 'review') {
            return stats.toReview > 0;
        }
        
        return stats.total >= mode.minCards;
    }

    getModeStatusClass(mode) {
        if (!this.isModeAvailable(mode)) return 'mode-disabled';
        if (mode.recommended) return 'mode-recommended';
        return 'mode-available';
    }

    getModeStatusText(mode) {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        
        if (!this.isModeAvailable(mode)) {
            if (mode.id === 'review') {
                return 'Aucune carte à réviser';
            }
            const needed = mode.minCards - stats.total;
            return `${needed} carte${needed > 1 ? 's' : ''} manquante${needed > 1 ? 's' : ''}`;
        }
        
        switch (mode.id) {
            case 'flashcards':
                return `${stats.total} carte${stats.total > 1 ? 's' : ''} disponible${stats.total > 1 ? 's' : ''}`;
            case 'learn':
                return `${stats.toReview} carte${stats.toReview > 1 ? 's' : ''} à apprendre`;
            case 'match':
                return `Jeu avec ${Math.min(stats.total, 12)} carte${Math.min(stats.total, 12) > 1 ? 's' : ''}`;
            case 'review':
                return `${stats.toReview} carte${stats.toReview > 1 ? 's' : ''} à réviser`;
            default:
                return '';
        }
    }

    getProgressInfo() {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        
        if (stats.total === 0) {
            return {
                percentage: 0,
                text: 'Aucune carte'
            };
        }
        
        const percentage = Math.round((stats.learned / stats.total) * 100);
        return {
            percentage,
            text: `${stats.learned}/${stats.total} cartes apprises (${percentage}%)`
        };
    }

    getRecommendedMode() {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        
        // Si il y a des cartes à réviser, recommander le mode révision
        if (stats.toReview > 0) {
            return this.studyModes.find(m => m.id === 'review');
        }
        
        // Sinon, recommander le mode flashcards s'il y a des cartes
        if (stats.total > 0) {
            return this.studyModes.find(m => m.id === 'flashcards');
        }
        
        return null;
    }

    get hasCards() {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        return stats.total > 0;
    }

    get completionPercentage() {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        if (stats.total === 0) return 0;
        return Math.round((stats.learned / stats.total) * 100);
    }

    get progressBarClass() {
        const percentage = this.completionPercentage;
        
        if (percentage === 0) return 'progress-new';
        if (percentage === 100) return 'progress-completed';
        if (percentage >= 75) return 'progress-excellent';
        if (percentage >= 50) return 'progress-good';
        return 'progress-learning';
    }

    getAvailableModes() {
        return this.studyModes.filter(mode => this.isModeAvailable(mode));
    }

    getUnavailableModes() {
        return this.studyModes.filter(mode => !this.isModeAvailable(mode));
    }

    getBestModeForUser() {
        const stats = this.props.deckStats || { total: 0, learned: 0, toReview: 0 };
        const available = this.getAvailableModes();
        
        if (available.length === 0) return null;
        
        // Logique de recommandation
        if (stats.toReview > 0) {
            const reviewMode = available.find(m => m.id === 'review');
            if (reviewMode) return reviewMode;
        }
        
        if (stats.total >= 6) {
            const matchMode = available.find(m => m.id === 'match');
            if (matchMode) return matchMode;
        }
        
        if (stats.total >= 4) {
            const learnMode = available.find(m => m.id === 'learn');
            if (learnMode) return learnMode;
        }
        
        const flashcardsMode = available.find(m => m.id === 'flashcards');
        return flashcardsMode || available[0];
    }
}