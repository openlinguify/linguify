// Gestion de la traduction automatique pour les cartes

// État de traduction
let translationState = {
    translatingFront: false,
    translatingBack: false
};

// Fonction pour traduire le texte
async function translateText(direction) {
    console.log('translateText appelée avec direction:', direction);
    
    const sourceField = direction === 'front' ? 'newCardFront' : 'newCardBack';
    const targetField = direction === 'front' ? 'newCardBack' : 'newCardFront';
    const sourceTextarea = document.getElementById(sourceField);
    const targetTextarea = document.getElementById(targetField);
    
    // Vérifications de base
    if (!sourceTextarea || !targetTextarea) {
        console.error('Champs de texte non trouvés');
        return;
    }
    
    const sourceText = sourceTextarea.value.trim();
    if (!sourceText) {
        showNotification('Veuillez d\'abord saisir du texte à traduire', 'warning');
        return;
    }
    
    if (sourceText.length > 1000) {
        showNotification('Le texte ne peut pas dépasser 1000 caractères', 'error');
        return;
    }
    
    // Déterminer les langues source et cible
    const sourceLangSelect = direction === 'front' ? 
        document.getElementById('newCardFrontLang') : 
        document.getElementById('newCardBackLang');
    const targetLangSelect = direction === 'front' ? 
        document.getElementById('newCardBackLang') : 
        document.getElementById('newCardFrontLang');
    
    let sourceLang = sourceLangSelect ? sourceLangSelect.value : '';
    let targetLang = targetLangSelect ? targetLangSelect.value : '';
    
    // Utiliser les langues par défaut du deck si pas de langue spécifique
    if (!sourceLang) {
        sourceLang = direction === 'front' ? getDeckDefaultFrontLang() : getDeckDefaultBackLang();
    }
    if (!targetLang) {
        targetLang = direction === 'front' ? getDeckDefaultBackLang() : getDeckDefaultFrontLang();
    }
    
    // Vérifier si les langues sont différentes
    if (sourceLang === targetLang) {
        showNotification('Les langues source et cible ne peuvent pas être identiques', 'warning');
        return;
    }
    
    // Mettre à jour l'état de chargement
    const propertyName = direction === 'front' ? 'translatingFront' : 'translatingBack';
    translationState[propertyName] = true;
    
    // Mettre à jour le bouton
    const btnId = direction === 'front' ? 'translateFrontBtn' : 'translateBackBtn';
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="spinner-border spinner-border-sm me-1"></i><span>Traduction...</span>';
    }
    
    try {
        // Debug information
        const csrfToken = getCSRFToken();
        console.log('CSRF Token:', csrfToken);
        console.log('Request URL:', '/revision/translate/');
        console.log('Request data:', {
            text: sourceText,
            source_language: sourceLang,
            target_language: targetLang
        });
        
        // Effectuer la requête de traduction
        const response = await fetch('/revision/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                text: sourceText,
                source_language: sourceLang,
                target_language: targetLang
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const responseText = await response.text();
        console.log('Response text:', responseText);
        
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            console.error('JSON parse error:', parseError);
            console.error('Response was not JSON:', responseText);
            throw new Error('Invalid JSON response from server');
        }
        
        if (response.ok && data.success) {
            // Succès - mettre à jour le champ cible
            targetTextarea.value = data.data.translated_text;
            
            // Afficher une notification de succès
            showNotification(
                `Traduction réussie de ${getLanguageName(data.data.source_language)} vers ${getLanguageName(data.data.target_language)}`, 
                'success'
            );
            
            // Focus sur le champ traduit
            targetTextarea.focus();
            
        } else {
            // Erreur de traduction
            const errorMessage = data.error || 'Erreur lors de la traduction';
            showNotification(errorMessage, 'error');
            console.error('Erreur de traduction:', data);
        }
        
    } catch (error) {
        console.error('Erreur de requête:', error);
        showNotification('Erreur de connexion lors de la traduction', 'error');
    } finally {
        // Réinitialiser l'état de chargement
        translationState[propertyName] = false;
        
        // Remettre le bouton à l'état normal
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-translate me-1"></i><span>Traduire</span>';
        }
    }
}

// Fonction pour obtenir le token CSRF
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        return token.value;
    }
    
    // Fallback - chercher dans les cookies
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    
    return '';
}

// Fonction pour obtenir la langue par défaut du recto du deck
function getDeckDefaultFrontLang() {
    // Cette fonction devrait récupérer la langue depuis le contexte du deck
    // Pour l'instant, on utilise une valeur par défaut
    return window.deckFrontLanguage || 'fr';
}

// Fonction pour obtenir la langue par défaut du verso du deck
function getDeckDefaultBackLang() {
    // Cette fonction devrait récupérer la langue depuis le contexte du deck
    // Pour l'instant, on utilise une valeur par défaut
    return window.deckBackLanguage || 'en';
}

// Fonction pour obtenir le nom de la langue
function getLanguageName(langCode) {
    const languages = {
        'fr': 'Français',
        'en': 'Anglais',
        'es': 'Espagnol',
        'it': 'Italien',
        'de': 'Allemand',
        'pt': 'Portugais',
        'nl': 'Néerlandais',
        'ru': 'Russe',
        'ja': 'Japonais',
        'ko': 'Coréen',
        'zh': 'Chinois',
        'ar': 'Arabe'
    };
    return languages[langCode] || langCode;
}

// Fonction pour afficher les notifications
function showNotification(message, type = 'info') {
    // Chercher un conteneur de notifications existant
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // Créer le conteneur s'il n'existe pas
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'position-fixed top-0 end-0 p-3';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${getBootstrapAlertClass(type)} alert-dismissible fade show`;
    notification.setAttribute('role', 'alert');
    notification.style.minWidth = '300px';
    
    const icon = getNotificationIcon(type);
    notification.innerHTML = `
        <i class="bi ${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Ajouter la notification au conteneur
    notificationContainer.appendChild(notification);
    
    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Fonction pour mapper les types de notification aux classes Bootstrap
function getBootstrapAlertClass(type) {
    const mapping = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return mapping[type] || 'info';
}

// Fonction pour obtenir l'icône de notification
function getNotificationIcon(type) {
    const mapping = {
        'success': 'bi-check-circle',
        'error': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-circle',
        'info': 'bi-info-circle'
    };
    return mapping[type] || 'bi-info-circle';
}

// Fonction simple pour inverser une carte
window.flipCard = async function(cardId) {
    console.log('Inversion carte:', cardId);
    
    // Trouver la carte dans le DOM
    const cardElement = document.querySelector(`[data-card-id="${cardId}"]`);
    const frontElement = cardElement?.querySelector('.card-front-text');
    const backElement = cardElement?.querySelector('.card-back-text');
    
    if (!cardElement || !frontElement || !backElement) {
        showNotification('Carte non trouvée', 'error');
        return;
    }
    
    // Ajouter animation de chargement
    const button = cardElement.querySelector('button');
    const originalContent = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="spinner-border spinner-border-sm"></i>';
    
    try {
        const response = await fetch(`/api/v1/revision/flashcards/${cardId}/flip_card/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Animation d'inversion - swap le contenu
            const frontText = frontElement.textContent;
            const backText = backElement.textContent;
            
            // Animation de fade out
            cardElement.style.transition = 'opacity 0.2s ease';
            cardElement.style.opacity = '0.5';
            
            setTimeout(() => {
                // Échanger le contenu
                frontElement.textContent = backText;
                backElement.textContent = frontText;
                
                // Animation de fade in
                cardElement.style.opacity = '1';
                
                showNotification('Carte inversée !', 'success');
            }, 200);
            
        } else {
            showNotification(data.detail || 'Erreur', 'error');
        }
    } catch (error) {
        showNotification('Erreur réseau', 'error');
        console.error(error);
    } finally {
        // Restaurer le bouton
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalContent;
        }, 400);
    }
};

// Exposer la fonction globalement
window.translateText = translateText;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de traduction chargé');
    
    // Raccourcis clavier pour la traduction
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + Shift + T pour traduire depuis le recto vers le verso
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
            event.preventDefault();
            const frontTextarea = document.getElementById('newCardFront');
            if (frontTextarea && frontTextarea.value.trim()) {
                translateText('front');
            }
        }
        
        // Ctrl/Cmd + Shift + R pour traduire depuis le verso vers le recto
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'R') {
            event.preventDefault();
            const backTextarea = document.getElementById('newCardBack');
            if (backTextarea && backTextarea.value.trim()) {
                translateText('back');
            }
        }
    });
});