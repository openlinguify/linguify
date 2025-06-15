// apps/revision/static/src/js/views/RevisionApp.js

const { Component, useState, useRef, onMounted, onWillUnmount } = owl;

/**
 * Composant principal de l'application Revision (Flashcards)
 * Migré depuis frontend/src/addons/flashcard/components/FlashcardMain.tsx
 */
export class RevisionApp extends Component {
    static template = "RevisionApp";

    setup() {
        // État local
        this.state = useState({
            decks: [],
            filteredDecks: [],
            searchQuery: "",
            isPageLoading: true,
            loadError: null,
            currentView: 'main', // 'main', 'deck', 'cards', 'study', 'explore'
            selectedDeck: null,
            selectedDeckId: null,
            studyMode: null
        });

        // Services
        this.revisionService = this.env.services.revision;
        this.notificationService = this.env.services.notification;

        // Refs
        this.searchInputRef = useRef("searchInput");

        // Configuration initiale depuis la page
        this.initializeFromPageConfig();

        // Lifecycle
        onMounted(() => {
            this.loadInitialData();
        });

        onWillUnmount(() => {
            // Cleanup si nécessaire
        });
    }

    /**
     * Initialise l'app selon la configuration de la page Django
     */
    initializeFromPageConfig() {
        const config = window.REVISION_CONFIG || {};
        
        if (config.viewType === 'deck' && config.deckId) {
            this.state.currentView = 'deck';
            this.state.selectedDeckId = config.deckId;
        } else if (config.viewType === 'explore') {
            this.state.currentView = 'explore';
        } else if (config.studyMode && config.deckId) {
            this.state.currentView = 'study';
            this.state.selectedDeckId = config.deckId;
            this.state.studyMode = config.studyMode;
        }
    }

    /**
     * Charge les données initiales selon la vue
     */
    async loadInitialData() {
        try {
            this.state.isPageLoading = true;
            this.state.loadError = null;

            if (this.state.currentView === 'deck' && this.state.selectedDeckId) {
                await this.loadDeckDetails(this.state.selectedDeckId);
            } else if (this.state.currentView === 'explore') {
                await this.loadPublicDecks();
            } else {
                await this.loadDecks();
            }
        } catch (error) {
            console.error('❌ Erreur lors du chargement initial:', error);
            this.state.loadError = 'Erreur lors du chargement';
        } finally {
            this.state.isPageLoading = false;
        }
    }

    // === MÉTHODES DE CHARGEMENT DES DONNÉES ===

    async loadDecks() {
        try {
            this.state.isPageLoading = true;
            this.state.loadError = null;

            const decks = await this.revisionService.getAllDecks();
            this.state.decks = decks;
            this.state.filteredDecks = decks;
            
            this.revisionService.logDebug('Decks chargés', decks.length);
        } catch (error) {
            this.revisionService.logError('Erreur lors du chargement des decks', error);
            this.state.loadError = 'Erreur lors du chargement des flashcards';
            
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors du chargement des flashcards');
            }
        } finally {
            this.state.isPageLoading = false;
        }
    }

    async loadDeckDetails(deckId) {
        try {
            this.state.isPageLoading = true;
            
            const deck = await this.revisionService.getDeckById(deckId);
            const cards = await this.revisionService.getDeckCards(deckId);
            
            this.state.selectedDeck = { ...deck, cards };
            this.state.selectedDeckId = deckId;
            
            this.revisionService.logDebug('Deck chargé', { name: deck.name, cards: cards.length });
        } catch (error) {
            this.revisionService.logError('Erreur lors du chargement du deck', error);
            this.state.loadError = 'Erreur lors du chargement du deck';
        } finally {
            this.state.isPageLoading = false;
        }
    }

    async loadPublicDecks() {
        try {
            this.state.isPageLoading = true;
            this.state.loadError = null;

            const decks = await this.revisionService.getPublicDecks();
            this.state.decks = decks;
            this.state.filteredDecks = decks;
            
            this.revisionService.logDebug('Decks publics chargés', decks.length);
        } catch (error) {
            this.revisionService.logError('Erreur lors du chargement des decks publics', error);
            this.state.loadError = 'Erreur lors du chargement des decks publics';
        } finally {
            this.state.isPageLoading = false;
        }
    }

    // === GESTION DE LA RECHERCHE ===

    onSearchInput(event) {
        const query = event.target.value;
        this.state.searchQuery = query;
        this.filterDecks(query);
    }

    filterDecks(query) {
        if (!query.trim()) {
            this.state.filteredDecks = this.state.decks;
        } else {
            const lowerQuery = query.toLowerCase();
            this.state.filteredDecks = this.state.decks.filter(deck =>
                deck.name.toLowerCase().includes(lowerQuery) ||
                (deck.description && deck.description.toLowerCase().includes(lowerQuery))
            );
        }
    }

    clearSearch() {
        this.state.searchQuery = "";
        this.state.filteredDecks = this.state.decks;
        if (this.searchInputRef.el) {
            this.searchInputRef.el.focus();
        }
    }

    // === NAVIGATION ENTRE LES VUES ===

    goToView(viewName, options = {}) {
        this.state.currentView = viewName;
        
        if (options.deckId) {
            this.loadDeckDetails(options.deckId);
        }
        
        if (options.studyMode) {
            this.state.studyMode = options.studyMode;
        }
        
        this.revisionService.logDebug('Navigation vers', { viewName, options });
    }

    goBack() {
        switch (this.state.currentView) {
            case 'deck':
            case 'explore':
                this.state.currentView = 'main';
                this.state.selectedDeck = null;
                this.state.selectedDeckId = null;
                break;
            case 'cards':
            case 'study':
                this.state.currentView = 'deck';
                this.state.studyMode = null;
                break;
            default:
                this.state.currentView = 'main';
        }
    }

    // === GESTION DES DECKS ===

    async onDeckSelect(deckId) {
        this.goToView('deck', { deckId });
    }

    async onCreateDeck() {
        try {
            const name = prompt('Nom du nouveau deck:');
            if (!name?.trim()) return;

            const description = prompt('Description (optionnelle):') || '';
            
            const newDeck = await this.revisionService.createDeck({
                name: name.trim(),
                description: description.trim()
            });

            // Recharger la liste des decks
            await this.loadDecks();
            
            if (this.notificationService.success) {
                this.notificationService.success(`Deck "${newDeck.name}" créé avec succès`);
            }
            
            // Aller directement vers le nouveau deck
            this.onDeckSelect(newDeck.id);
            
        } catch (error) {
            this.revisionService.logError('Erreur lors de la création du deck', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors de la création du deck');
            }
        }
    }

    async onDeleteDeck(deckId) {
        try {
            const deck = this.state.decks.find(d => d.id === deckId);
            if (!deck) return;

            const confirmed = confirm(`Êtes-vous sûr de vouloir supprimer le deck "${deck.name}" ?`);
            if (!confirmed) return;

            await this.revisionService.deleteDeck(deckId);
            
            // Recharger la liste
            await this.loadDecks();
            
            if (this.notificationService.success) {
                this.notificationService.success(`Deck "${deck.name}" supprimé`);
            }
            
            // Retourner à la vue principale si on était sur ce deck
            if (this.state.selectedDeckId === deckId) {
                this.goToView('main');
            }
            
        } catch (error) {
            this.revisionService.logError('Erreur lors de la suppression du deck', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors de la suppression du deck');
            }
        }
    }

    async onToggleDeckPublic(deckId) {
        try {
            const deck = this.state.decks.find(d => d.id === deckId);
            if (!deck) return;

            const updatedDeck = await this.revisionService.toggleDeckPublic(deckId);
            
            // Mettre à jour dans la liste locale
            const index = this.state.decks.findIndex(d => d.id === deckId);
            if (index !== -1) {
                this.state.decks[index] = updatedDeck;
                this.filterDecks(this.state.searchQuery);
            }
            
            // Mettre à jour le deck sélectionné si c'est le même
            if (this.state.selectedDeckId === deckId) {
                this.state.selectedDeck = { ...this.state.selectedDeck, ...updatedDeck };
            }
            
            const status = updatedDeck.is_public ? 'public' : 'privé';
            if (this.notificationService.success) {
                this.notificationService.success(`Deck "${deck.name}" maintenant ${status}`);
            }
            
        } catch (error) {
            this.revisionService.logError('Erreur lors de la modification de la visibilité', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors de la modification de la visibilité');
            }
        }
    }

    async onCloneDeck(deckId) {
        try {
            const deck = this.state.decks.find(d => d.id === deckId);
            if (!deck) return;

            const clonedDeck = await this.revisionService.cloneDeck(deckId);
            
            // Recharger la liste des decks
            await this.loadDecks();
            
            if (this.notificationService.success) {
                this.notificationService.success(`Deck "${deck.name}" cloné avec succès`);
            }
            
            // Aller vers le deck cloné
            this.onDeckSelect(clonedDeck.id);
            
        } catch (error) {
            this.revisionService.logError('Erreur lors du clonage du deck', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors du clonage du deck');
            }
        }
    }

    // === GESTION DES CARTES ===

    async onCreateCard() {
        if (!this.state.selectedDeck) return;

        try {
            const frontText = prompt('Texte recto:');
            if (!frontText?.trim()) return;

            const backText = prompt('Texte verso:');
            if (!backText?.trim()) return;

            await this.revisionService.createCard({
                deck: this.state.selectedDeck.id,
                front_text: frontText.trim(),
                back_text: backText.trim()
            });

            // Recharger les cartes du deck
            await this.loadDeckDetails(this.state.selectedDeck.id);
            
            if (this.notificationService.success) {
                this.notificationService.success('Carte créée avec succès');
            }
            
        } catch (error) {
            this.revisionService.logError('Erreur lors de la création de la carte', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors de la création de la carte');
            }
        }
    }

    async onUpdateCard(cardId, data) {
        try {
            await this.revisionService.updateCard(cardId, data);
            
            // Recharger les cartes du deck
            if (this.state.selectedDeck) {
                await this.loadDeckDetails(this.state.selectedDeck.id);
            }
            
            if (this.notificationService.success) {
                this.notificationService.success('Carte mise à jour');
            }
            
        } catch (error) {
            this.revisionService.logError('Erreur lors de la mise à jour de la carte', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors de la mise à jour de la carte');
            }
        }
    }

    async onDeleteCard(cardId) {
        try {
            const card = this.state.selectedDeck?.cards?.find(c => c.id === cardId);
            if (!card) return;

            const confirmed = confirm('Êtes-vous sûr de vouloir supprimer cette carte ?');
            if (!confirmed) return;

            await this.revisionService.deleteCard(cardId);
            
            // Recharger les cartes du deck
            await this.loadDeckDetails(this.state.selectedDeck.id);
            
            if (this.notificationService.success) {
                this.notificationService.success('Carte supprimée');
            }
            
        } catch (error) {
            this.revisionService.logError('Erreur lors de la suppression de la carte', error);
            if (this.notificationService.error) {
                this.notificationService.error('Erreur lors de la suppression de la carte');
            }
        }
    }

    // === GESTION DES MODES D'ÉTUDE ===

    onModeSelect(modeId, options = {}) {
        const url = `/revision/deck/${this.state.selectedDeck.id}/study/${modeId}/`;
        window.location.href = url;
    }

    // === ACTIONS GÉNÉRALES ===

    async onRefresh() {
        if (this.state.currentView === 'main') {
            await this.loadDecks();
        } else if (this.state.currentView === 'explore') {
            await this.loadPublicDecks();
        } else if (this.state.selectedDeckId) {
            await this.loadDeckDetails(this.state.selectedDeckId);
        }
    }

    onRetry() {
        this.loadInitialData();
    }

    // === GETTERS POUR LES TEMPLATES ===

    get hasDecks() {
        return this.state.filteredDecks.length > 0;
    }

    get isMainView() {
        return this.state.currentView === 'main';
    }

    get isDeckView() {
        return this.state.currentView === 'deck';
    }

    get isExploreView() {
        return this.state.currentView === 'explore';
    }

    get isStudyView() {
        return this.state.currentView === 'study';
    }

    get showSearchBar() {
        return !this.state.isPageLoading && !this.state.loadError;
    }

    get deckStats() {
        if (!this.state.selectedDeck || !this.state.selectedDeck.cards) {
            return { total: 0, learned: 0, toReview: 0 };
        }

        const cards = this.state.selectedDeck.cards;
        return {
            total: cards.length,
            learned: cards.filter(c => c.learned).length,
            toReview: cards.filter(c => !c.learned).length
        };
    }

    get pageTitle() {
        switch (this.state.currentView) {
            case 'deck':
                return this.state.selectedDeck ? `📖 ${this.state.selectedDeck.name}` : '📖 Deck';
            case 'explore':
                return '🌐 Explorer les decks publics';
            case 'study':
                return this.state.selectedDeck ? `🎯 Étudier: ${this.state.selectedDeck.name}` : '🎯 Étude';
            default:
                return '📚 Mes Flashcards';
        }
    }
}