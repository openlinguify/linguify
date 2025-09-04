// JavaScript général pour Language Learning
document.addEventListener('DOMContentLoaded', function() {
    console.log('Language Learning app loaded');
    
    // Confirmation de suppression
    const deleteButtons = document.querySelectorAll('.btn-outline-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet item ?')) {
                e.preventDefault();
            }
        });
    });
    
    // Animation des cartes
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fade-in');
    });
});

// API Helper
class LanguagelearningAPI {
    static async getItems() {
        try {
            const response = await fetch('/language-learning/api/items/');
            return await response.json();
        } catch (error) {
            console.error('Error fetching items:', error);
            return null;
        }
    }
    
    static async createItem(data) {
        try {
            const response = await fetch('/language-learning/api/items/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating item:', error);
            return null;
        }
    }
    
    static async updateItem(id, data) {
        try {
            const response = await fetch(`/language-learning/api/items/${id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error updating item:', error);
            return null;
        }
    }
    
    static async deleteItem(id) {
        try {
            const response = await fetch(`/language-learning/api/items/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            });
            return response.ok;
        } catch (error) {
            console.error('Error deleting item:', error);
            return false;
        }
    }
}
