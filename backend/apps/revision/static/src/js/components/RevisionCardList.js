// apps/revision/static/src/js/components/RevisionCardList.js

const { Component, useState, useRef } = owl;

/**
 * Composant pour afficher et gérer une liste de cartes de révision/flashcards
 * Migré depuis frontend flashcard components
 */
export class RevisionCardList extends Component {
    static template = "RevisionCardList";
    static props = {
        cards: Array,
        deckId: Number,
        onCardUpdate: Function,
        onCardDelete: { type: Function, optional: true },
        onCardCreate: { type: Function, optional: true },
        readonly: { type: Boolean, optional: true }
    };

    setup() {
        this.state = useState({
            // Pagination
            currentPage: 1,
            pageSize: 20,
            
            // Tri
            sortConfig: {
                key: 'front_text',
                direction: 'asc'
            },
            
            // Filtrage
            filterType: 'all', // 'all', 'new', 'review', 'learned'
            searchQuery: '',
            
            // Édition
            editingCard: null,
            isCreating: false,
            
            // Sélection
            selectedCards: new Set()
        });

        this.searchInputRef = useRef("searchInput");
    }

    // === GESTION DU TRI ===

    onSort(key) {
        if (this.state.sortConfig.key === key) {
            this.state.sortConfig.direction = 
                this.state.sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sortConfig.key = key;
            this.state.sortConfig.direction = 'asc';
        }
    }

    getSortIcon(key) {
        if (this.state.sortConfig.key !== key) return '↕️';
        return this.state.sortConfig.direction === 'asc' ? '↑' : '↓';
    }

    // === GESTION DU FILTRAGE ===

    onFilterChange(filterType) {
        this.state.filterType = filterType;
        this.state.currentPage = 1;
    }

    onSearchInput(event) {
        this.state.searchQuery = event.target.value;
        this.state.currentPage = 1;
    }

    clearSearch() {
        this.state.searchQuery = '';
        if (this.searchInputRef.el) {
            this.searchInputRef.el.focus();
        }
    }

    // === TRAITEMENT DES DONNÉES ===

    get filteredAndSortedCards() {
        let cards = [...this.props.cards];

        // Filtrage par type
        switch (this.state.filterType) {
            case 'new':
                cards = cards.filter(card => !card.learned && card.review_count === 0);
                break;
            case 'review':
                cards = cards.filter(card => !card.learned && card.review_count > 0);
                break;
            case 'learned':
                cards = cards.filter(card => card.learned);
                break;
        }

        // Filtrage par recherche
        if (this.state.searchQuery.trim()) {
            const query = this.state.searchQuery.toLowerCase();
            cards = cards.filter(card =>
                card.front_text.toLowerCase().includes(query) ||
                card.back_text.toLowerCase().includes(query)
            );
        }

        // Tri
        cards.sort((a, b) => {
            const { key, direction } = this.state.sortConfig;
            let aValue = a[key] || '';
            let bValue = b[key] || '';

            // Traitement spécial pour les dates
            if (key === 'last_reviewed' || key.includes('_at')) {
                aValue = aValue ? new Date(aValue) : new Date(0);
                bValue = bValue ? new Date(bValue) : new Date(0);
            }

            // Traitement spécial pour les booléens
            if (typeof aValue === 'boolean') {
                aValue = aValue ? 1 : 0;
                bValue = bValue ? 1 : 0;
            }

            let comparison = 0;
            if (aValue > bValue) comparison = 1;
            if (aValue < bValue) comparison = -1;

            return direction === 'desc' ? -comparison : comparison;
        });

        return cards;
    }

    get paginatedCards() {
        const start = (this.state.currentPage - 1) * this.state.pageSize;
        const end = start + this.state.pageSize;
        return this.filteredAndSortedCards.slice(start, end);
    }

    get totalPages() {
        return Math.ceil(this.filteredAndSortedCards.length / this.state.pageSize);
    }

    get paginationInfo() {
        const total = this.filteredAndSortedCards.length;
        const start = (this.state.currentPage - 1) * this.state.pageSize + 1;
        const end = Math.min(start + this.state.pageSize - 1, total);
        
        return { start, end, total };
    }

    // === GESTION DE LA PAGINATION ===

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.state.currentPage = page;
        }
    }

    nextPage() {
        this.goToPage(this.state.currentPage + 1);
    }

    prevPage() {
        this.goToPage(this.state.currentPage - 1);
    }

    // === GESTION DE L'ÉDITION ===

    startEditing(card) {
        if (this.props.readonly) return;
        
        this.state.editingCard = {
            id: card.id,
            front_text: card.front_text,
            back_text: card.back_text,
            learned: card.learned
        };
    }

    cancelEditing() {
        this.state.editingCard = null;
    }

    async saveEditing() {
        if (!this.state.editingCard) return;

        try {
            const updatedData = {
                front_text: this.state.editingCard.front_text.trim(),
                back_text: this.state.editingCard.back_text.trim(),
                learned: this.state.editingCard.learned
            };

            if (!updatedData.front_text || !updatedData.back_text) {
                alert('Le recto et le verso sont requis');
                return;
            }

            await this.props.onCardUpdate(this.state.editingCard.id, updatedData);
            this.state.editingCard = null;
        } catch (error) {
            console.error('❌ Erreur lors de la sauvegarde de la carte:', error);
            alert('Erreur lors de la sauvegarde de la carte');
        }
    }

    // === GESTION DES ACTIONS ===

    onEditCard(card, event) {
        event.stopPropagation();
        this.startEditing(card);
    }

    onDeleteCard(card, event) {
        event.stopPropagation();
        if (this.props.onCardDelete) {
            this.props.onCardDelete(card.id);
        }
    }

    async onToggleLearned(card, event) {
        event.stopPropagation();
        try {
            await this.props.onCardUpdate(card.id, { learned: !card.learned });
        } catch (error) {
            console.error('❌ Erreur lors de la mise à jour de l\'état d\'apprentissage:', error);
        }
    }

    // === GESTION DES ENTRÉES ===

    onEditFrontInput(event) {
        if (this.state.editingCard) {
            this.state.editingCard.front_text = event.target.value;
        }
    }

    onEditBackInput(event) {
        if (this.state.editingCard) {
            this.state.editingCard.back_text = event.target.value;
        }
    }

    onEditLearnedChange(event) {
        if (this.state.editingCard) {
            this.state.editingCard.learned = event.target.checked;
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

    // === GESTION DE LA SÉLECTION ===

    onCardSelect(card, event) {
        if (this.props.readonly) return;
        if (event.target.type === 'checkbox') return;

        const cardId = card.id;
        if (this.state.selectedCards.has(cardId)) {
            this.state.selectedCards.delete(cardId);
        } else {
            this.state.selectedCards.add(cardId);
        }
    }

    onSelectAll(event) {
        if (this.props.readonly) return;
        
        if (event.target.checked) {
            this.paginatedCards.forEach(card => {
                this.state.selectedCards.add(card.id);
            });
        } else {
            this.paginatedCards.forEach(card => {
                this.state.selectedCards.delete(card.id);
            });
        }
    }

    // === HELPERS ===

    isEditing(card) {
        return this.state.editingCard?.id === card.id;
    }

    isSelected(card) {
        return this.state.selectedCards.has(card.id);
    }

    get hasSelectedCards() {
        return this.state.selectedCards.size > 0;
    }

    get selectedCardsCount() {
        return this.state.selectedCards.size;
    }

    formatDate(dateString) {
        if (!dateString) return 'Jamais';
        
        try {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }).format(date);
        } catch (error) {
            return dateString;
        }
    }

    getCardStatusClass(card) {
        if (card.learned) return 'status-learned';
        if (card.review_count === 0) return 'status-new';
        return 'status-review';
    }

    getCardStatusText(card) {
        if (card.learned) return 'Apprise';
        if (card.review_count === 0) return 'Nouvelle';
        return `À réviser (${card.review_count} fois)`;
    }

    getFilterCounts() {
        const cards = this.props.cards;
        return {
            all: cards.length,
            new: cards.filter(c => !c.learned && c.review_count === 0).length,
            review: cards.filter(c => !c.learned && c.review_count > 0).length,
            learned: cards.filter(c => c.learned).length
        };
    }

    get canEdit() {
        return !this.props.readonly;
    }

    get showEditControls() {
        return this.canEdit && this.props.onCardUpdate;
    }

    get showDeleteButton() {
        return this.canEdit && this.props.onCardDelete;
    }
}