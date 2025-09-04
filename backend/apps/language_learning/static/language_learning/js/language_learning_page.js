// JavaScript spécifique pour la page Language Learning
class LanguagelearningPage {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('Language Learning page initialized');
        this.setupEventListeners();
        this.loadInitialData();
        this.setupAnimations();
    }
    
    setupEventListeners() {
        // Gestionnaire pour les boutons d'action
        const actionButtons = document.querySelectorAll('.language_learning-btn-primary');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleActionClick(e);
            });
        });
        
        // Gestionnaire pour les cartes d'items
        const itemCards = document.querySelectorAll('.language_learning-item-card');
        itemCards.forEach(card => {
            card.addEventListener('click', (e) => {
                this.handleCardClick(e);
            });
        });
        
        // Gestionnaire pour la recherche
        const searchInput = document.querySelector('#language_learning-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
    }
    
    async loadInitialData() {
        try {
            const data = await LanguagelearningAPI.getItems();
            if (data) {
                this.renderItems(data.items);
            }
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }
    
    renderItems(items) {
        const container = document.querySelector('.language_learning-item-grid');
        if (!container) return;
        
        if (items.length === 0) {
            this.showEmptyState();
            return;
        }
        
        container.innerHTML = items.map(item => `
            <div class="language_learning-item-card language_learning-animate-in" data-item-id="${item.id}">
                <h5>${item.title}</h5>
                <p>${item.description || 'Aucune description'}</p>
                <small class="text-muted">
                    Créé le ${new Date(item.created_at).toLocaleDateString('fr-FR')}
                </small>
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="language_learningPage.editItem(${item.id})">
                        <i class="bi bi-pencil"></i> Modifier
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="language_learningPage.deleteItem(${item.id})">
                        <i class="bi bi-trash"></i> Supprimer
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    showEmptyState() {
        const container = document.querySelector('.language_learning-item-grid');
        if (!container) return;
        
        container.innerHTML = `
            <div class="language_learning-empty-state">
                <div class="language_learning-empty-icon">
                    <i class="bi bi-inbox"></i>
                </div>
                <h3>Aucun item</h3>
                <p>Commencez par créer votre premier item.</p>
                <button class="language_learning-btn-primary" onclick="language_learningPage.createItem()">
                    <i class="bi bi-plus"></i> Créer le premier item
                </button>
            </div>
        `;
    }
    
    setupAnimations() {
        // Observer pour les animations d'apparition
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('language_learning-animate-in');
                }
            });
        }, { threshold: 0.1 });
        
        // Observer tous les éléments avec la classe d'animation
        const animateElements = document.querySelectorAll('.language_learning-item-card');
        animateElements.forEach(el => observer.observe(el));
    }
    
    handleActionClick(e) {
        const action = e.target.dataset.action;
        switch (action) {
            case 'create':
                this.createItem();
                break;
            case 'refresh':
                this.loadInitialData();
                break;
            default:
                console.log('Action clicked:', action);
        }
    }
    
    handleCardClick(e) {
        const card = e.target.closest('.language_learning-item-card');
        if (!card) return;
        
        const itemId = card.dataset.itemId;
        console.log('Card clicked, item ID:', itemId);
        // Ajouter logique spécifique ici
    }
    
    handleSearch(query) {
        const cards = document.querySelectorAll('.language_learning-item-card');
        cards.forEach(card => {
            const title = card.querySelector('h5').textContent.toLowerCase();
            const description = card.querySelector('p').textContent.toLowerCase();
            const matches = title.includes(query.toLowerCase()) || description.includes(query.toLowerCase());
            
            card.style.display = matches ? 'block' : 'none';
        });
    }
    
    static async createItem() {
        // Redirect to create page or open modal
        window.location.href = '/language-learning/create/';
    }
    
    static async editItem(id) {
        // Redirect to edit page or open modal
        window.location.href = `/language-learning/edit/${id}/`;
    }
    
    static async deleteItem(id) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet item ?')) {
            return;
        }
        
        const success = await LanguagelearningAPI.deleteItem(id);
        if (success) {
            // Refresh the page or remove the item from DOM
            window.location.reload();
        } else {
            alert('Erreur lors de la suppression');
        }
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.language_learning-page')) {
        window.language_learningPage = new LanguagelearningPage();
    }
});
