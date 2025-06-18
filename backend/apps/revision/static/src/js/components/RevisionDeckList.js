// apps/revision/static/src/js/components/RevisionDeckList.js

const { Component, useState } = owl;

/**
 * Composant pour afficher la liste des decks de révision/flashcards
 * Migré depuis frontend flashcard components
 */
export class RevisionDeckList extends Component {
    static template = "RevisionDeckList";
    static props = {
        decks: Array,
        onDeckSelect: Function,
        onDeckUpdate: { type: Function, optional: true },
        onDeckDelete: { type: Function, optional: true },
        onDeckTogglePublic: { type: Function, optional: true },
        onDeckClone: { type: Function, optional: true },
        isPublicView: { type: Boolean, optional: true }
    };

    setup() {
        this.state = useState({
            editingDeck: null,
            isCreating: false
        });
    }

    // === GESTION DE L'ÉDITION ===

    startEditing(deck) {
        this.state.editingDeck = {
            id: deck.id,
            name: deck.name,
            description: deck.description || ''
        };
    }

    cancelEditing() {
        this.state.editingDeck = null;
    }

    async saveEditing() {
        if (!this.state.editingDeck) return;

        try {
            const updatedData = {
                name: this.state.editingDeck.name.trim(),
                description: this.state.editingDeck.description.trim()
            };

            // Valider les données
            if (!updatedData.name) {
                alert('Le nom du deck est requis');
                return;
            }

            // Appeler le parent pour la mise à jour
            if (this.props.onDeckUpdate) {
                await this.props.onDeckUpdate(this.state.editingDeck.id, updatedData);
            }

            this.state.editingDeck = null;
        } catch (error) {
            console.error('❌ Erreur lors de la sauvegarde:', error);
            alert('Erreur lors de la sauvegarde du deck');
        }
    }

    // === GESTION DES ACTIONS ===

    onDeckClick(deck) {
        if (this.state.editingDeck?.id === deck.id) return;
        this.props.onDeckSelect(deck.id);
    }

    onDeleteDeck(deck, event) {
        event.stopPropagation();
        if (this.props.onDeckDelete) {
            this.props.onDeckDelete(deck.id);
        }
    }

    onTogglePublic(deck, event) {
        event.stopPropagation();
        if (this.props.onDeckTogglePublic) {
            this.props.onDeckTogglePublic(deck.id);
        }
    }

    onCloneDeck(deck, event) {
        event.stopPropagation();
        if (this.props.onDeckClone) {
            this.props.onDeckClone(deck.id);
        }
    }

    onEditDeck(deck, event) {
        event.stopPropagation();
        this.startEditing(deck);
    }

    // === GESTION DES ENTRÉES ===

    onEditNameInput(event) {
        if (this.state.editingDeck) {
            this.state.editingDeck.name = event.target.value;
        }
    }

    onEditDescriptionInput(event) {
        if (this.state.editingDeck) {
            this.state.editingDeck.description = event.target.value;
        }
    }

    onEditKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.saveEditing();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            this.cancelEditing();
        }
    }

    // === HELPERS ===

    isEditing(deck) {
        return this.state.editingDeck?.id === deck.id;
    }

    getDeckCardCount(deck) {
        return deck.card_count || deck.cards?.length || 0;
    }

    getDeckLearnedCount(deck) {
        return deck.learned_count || deck.cards?.filter(c => c.learned).length || 0;
    }

    formatDate(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            }).format(date);
        } catch (error) {
            return dateString;
        }
    }

    getProgressPercentage(deck) {
        const total = this.getDeckCardCount(deck);
        const learned = this.getDeckLearnedCount(deck);
        
        if (total === 0) return 0;
        return Math.round((learned / total) * 100);
    }

    getDeckStatusClass(deck) {
        const percentage = this.getProgressPercentage(deck);
        
        if (percentage === 0) return 'status-new';
        if (percentage === 100) return 'status-completed';
        if (percentage >= 50) return 'status-good';
        return 'status-learning';
    }

    getDeckVisibilityIcon(deck) {
        return deck.is_public ? '🌐' : '🔒';
    }

    getDeckVisibilityText(deck) {
        return deck.is_public ? 'Public' : 'Privé';
    }

    getDeckOwnerInfo(deck) {
        if (this.props.isPublicView && deck.user) {
            return `Par ${deck.user.username || 'Anonyme'}`;
        }
        return '';
    }

    canEdit(deck) {
        // Dans la vue publique, on ne peut pas éditer
        if (this.props.isPublicView) return false;
        
        // Sinon, on peut éditer ses propres decks
        return true;
    }

    canDelete(deck) {
        // Dans la vue publique, on ne peut pas supprimer
        if (this.props.isPublicView) return false;
        
        // Sinon, on peut supprimer ses propres decks
        return true;
    }

    canTogglePublic(deck) {
        // Dans la vue publique, on ne peut pas changer la visibilité
        if (this.props.isPublicView) return false;
        
        // Sinon, on peut changer la visibilité de ses propres decks
        return true;
    }

    getAvailableActions(deck) {
        const actions = [];
        
        if (this.props.isPublicView) {
            // Actions pour les decks publics
            if (this.props.onDeckClone) {
                actions.push({
                    type: 'clone',
                    icon: '📋',
                    title: 'Cloner ce deck',
                    handler: (e) => this.onCloneDeck(deck, e)
                });
            }
        } else {
            // Actions pour ses propres decks
            if (this.canTogglePublic(deck)) {
                actions.push({
                    type: 'toggle-public',
                    icon: this.getDeckVisibilityIcon(deck),
                    title: this.getDeckVisibilityText(deck),
                    handler: (e) => this.onTogglePublic(deck, e)
                });
            }
            
            if (this.canEdit(deck)) {
                actions.push({
                    type: 'edit',
                    icon: '✏️',
                    title: 'Modifier',
                    handler: (e) => this.onEditDeck(deck, e)
                });
            }
            
            if (this.canDelete(deck)) {
                actions.push({
                    type: 'delete',
                    icon: '🗑️',
                    title: 'Supprimer',
                    class: 'btn-danger',
                    handler: (e) => this.onDeleteDeck(deck, e)
                });
            }
        }
        
        return actions;
    }
}