// Translation and card flip management

// ==================== i18n Dictionary ====================
const i18n = {
    en: {
        'please_enter_text': 'Please enter text to translate',
        'text_too_long': 'Text cannot exceed 1000 characters',
        'same_languages': 'Source and target languages cannot be the same',
        'translating': 'Translating...',
        'translate': 'Translate',
        'translation_success': 'Successfully translated from {from} to {to}',
        'translation_error': 'Error during translation',
        'connection_error': 'Connection error during translation',
        'invalid_card_id': 'Cannot flip card: Invalid ID',
        'card_elements_not_found': 'Cannot find card elements',
        'flip_button_not_found': 'Cannot find flip button',
        'flip_error': 'Error during flip',
        'card_flipped_temp': 'Card flipped (temporary)',
        'card_flipped': 'Card flipped!',
        'network_error': 'Network error',
        'lang_fr': 'French',
        'lang_en': 'English',
        'lang_es': 'Spanish',
        'lang_nl': 'Dutch'
    },
    fr: {
        'please_enter_text': 'Veuillez d\'abord saisir du texte à traduire',
        'text_too_long': 'Le texte ne peut pas dépasser 1000 caractères',
        'same_languages': 'Les langues source et cible ne peuvent pas être identiques',
        'translating': 'Traduction...',
        'translate': 'Traduire',
        'translation_success': 'Traduction réussie de {from} vers {to}',
        'translation_error': 'Erreur lors de la traduction',
        'connection_error': 'Erreur de connexion lors de la traduction',
        'invalid_card_id': 'Impossible d\'inverser la carte: ID invalide',
        'card_elements_not_found': 'Impossible de trouver les éléments de la carte',
        'flip_button_not_found': 'Impossible de trouver le bouton d\'inversion',
        'flip_error': 'Erreur lors de l\'inversion',
        'card_flipped_temp': 'Carte inversée (temporaire)',
        'card_flipped': 'Carte inversée !',
        'network_error': 'Erreur réseau',
        'lang_fr': 'Français',
        'lang_en': 'Anglais',
        'lang_es': 'Espagnol',
        'lang_nl': 'Néerlandais'
    },
    es: {
        'please_enter_text': 'Por favor, introduzca el texto a traducir',
        'text_too_long': 'El texto no puede superar los 1000 caracteres',
        'same_languages': 'Los idiomas de origen y destino no pueden ser iguales',
        'translating': 'Traduciendo...',
        'translate': 'Traducir',
        'translation_success': 'Traducción exitosa de {from} a {to}',
        'translation_error': 'Error durante la traducción',
        'connection_error': 'Error de conexión durante la traducción',
        'invalid_card_id': 'No se puede voltear la tarjeta: ID inválido',
        'card_elements_not_found': 'No se pueden encontrar los elementos de la tarjeta',
        'flip_button_not_found': 'No se puede encontrar el botón de volteo',
        'flip_error': 'Error al voltear',
        'card_flipped_temp': 'Tarjeta volteada (temporal)',
        'card_flipped': '¡Tarjeta volteada!',
        'network_error': 'Error de red',
        'lang_fr': 'Francés',
        'lang_en': 'Inglés',
        'lang_es': 'Español',
        'lang_nl': 'Holandés'
    },
    nl: {
        'please_enter_text': 'Voer eerst tekst in om te vertalen',
        'text_too_long': 'Tekst mag niet langer zijn dan 1000 tekens',
        'same_languages': 'Bron- en doeltaal kunnen niet hetzelfde zijn',
        'translating': 'Vertalen...',
        'translate': 'Vertalen',
        'translation_success': 'Succesvol vertaald van {from} naar {to}',
        'translation_error': 'Fout bij vertaling',
        'connection_error': 'Verbindingsfout bij vertaling',
        'invalid_card_id': 'Kan kaart niet omdraaien: Ongeldig ID',
        'card_elements_not_found': 'Kan kaartelementen niet vinden',
        'flip_button_not_found': 'Kan omdraaiknop niet vinden',
        'flip_error': 'Fout bij omdraaien',
        'card_flipped_temp': 'Kaart omgedraaid (tijdelijk)',
        'card_flipped': 'Kaart omgedraaid!',
        'network_error': 'Netwerkfout',
        'lang_fr': 'Frans',
        'lang_en': 'Engels',
        'lang_es': 'Spaans',
        'lang_nl': 'Nederlands'
    }
};

// Get user language from Django or browser
function getUserLanguage() {
    const djangoLang = document.documentElement.lang || document.querySelector('html')?.getAttribute('lang');
    if (djangoLang && i18n[djangoLang]) {
        return djangoLang;
    }
    const browserLang = navigator.language.split('-')[0];
    if (i18n[browserLang]) {
        return browserLang;
    }
    return 'en';
}

// Translation function
function t(key, replacements = {}) {
    const lang = getUserLanguage();
    let text = i18n[lang]?.[key] || i18n['en'][key] || key;
    Object.keys(replacements).forEach(placeholder => {
        text = text.replace(`{${placeholder}}`, replacements[placeholder]);
    });
    return text;
}

// ==================== Translation State ====================
let translationState = {
    translatingFront: false,
    translatingBack: false
};

// ==================== Text Translation Function ====================
async function translateText(direction) {
    console.log('translateText called with direction:', direction);

    const sourceField = direction === 'front' ? 'newCardFront' : 'newCardBack';
    const targetField = direction === 'front' ? 'newCardBack' : 'newCardFront';
    const sourceTextarea = document.getElementById(sourceField);
    const targetTextarea = document.getElementById(targetField);

    // Basic validation
    if (!sourceTextarea || !targetTextarea) {
        console.error('Text fields not found');
        return;
    }

    const sourceText = sourceTextarea.value.trim();
    if (!sourceText) {
        showNotification(t('please_enter_text'), 'warning');
        return;
    }

    if (sourceText.length > 1000) {
        showNotification(t('text_too_long'), 'error');
        return;
    }

    // Determine source and target languages
    const sourceLangSelect = direction === 'front' ?
        document.getElementById('newCardFrontLang') :
        document.getElementById('newCardBackLang');
    const targetLangSelect = direction === 'front' ?
        document.getElementById('newCardBackLang') :
        document.getElementById('newCardFrontLang');

    let sourceLang = sourceLangSelect ? sourceLangSelect.value : '';
    let targetLang = targetLangSelect ? targetLangSelect.value : '';

    // Use deck default languages if no specific language
    if (!sourceLang) {
        sourceLang = direction === 'front' ? getDeckDefaultFrontLang() : getDeckDefaultBackLang();
    }
    if (!targetLang) {
        targetLang = direction === 'front' ? getDeckDefaultBackLang() : getDeckDefaultFrontLang();
    }

    // Check if languages are different
    if (sourceLang === targetLang) {
        showNotification(t('same_languages'), 'warning');
        return;
    }

    // Update loading state
    const propertyName = direction === 'front' ? 'translatingFront' : 'translatingBack';
    translationState[propertyName] = true;

    // Update button
    const btnId = direction === 'front' ? 'translateFrontBtn' : 'translateBackBtn';
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="spinner-border spinner-border-sm me-1"></i><span>${t('translating')}</span>`;
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

        // Make translation request
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
            // Success - update target field
            targetTextarea.value = data.data.translated_text;

            // Show success notification
            showNotification(
                t('translation_success', {
                    from: getLanguageName(data.data.source_language),
                    to: getLanguageName(data.data.target_language)
                }),
                'success'
            );

            // Focus on translated field
            targetTextarea.focus();

        } else {
            // Translation error
            const errorMessage = data.error || t('translation_error');
            showNotification(errorMessage, 'error');
            console.error('Translation error:', data);
        }

    } catch (error) {
        console.error('Request error:', error);
        showNotification(t('connection_error'), 'error');
    } finally {
        // Reset loading state
        translationState[propertyName] = false;

        // Reset button to normal state
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="bi bi-translate me-1"></i><span>${t('translate')}</span>`;
        }
    }
}

// ==================== Helper Functions ====================

// Get CSRF token
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        return token.value;
    }

    // Fallback - search in cookies
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }

    return '';
}

// Get deck default front language
function getDeckDefaultFrontLang() {
    return window.deckFrontLanguage || 'fr';
}

// Get deck default back language
function getDeckDefaultBackLang() {
    return window.deckBackLanguage || 'en';
}

// Get language name translated
function getLanguageName(langCode) {
    return t(`lang_${langCode}`) || langCode;
}

// Show notification
function showNotification(message, type = 'info') {
    let notificationContainer = document.getElementById('notification-container');

    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'position-fixed top-0 end-0 p-3';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }

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

    notificationContainer.appendChild(notification);

    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Map notification types to Bootstrap classes
function getBootstrapAlertClass(type) {
    const mapping = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return mapping[type] || 'info';
}

// Get notification icon
function getNotificationIcon(type) {
    const mapping = {
        'success': 'bi-check-circle',
        'error': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-circle',
        'info': 'bi-info-circle'
    };
    return mapping[type] || 'bi-info-circle';
}

// ==================== Card Flip Function ====================
// This function is called when user clicks the swap button (⇄) in the card list
window.flipCardTranslation = async function(cardId, event) {
    console.log('Card flip:', cardId, 'Event:', event);

    // If cardId is not valid, try to find it from clicked element
    if (!cardId || cardId === 'undefined' || cardId === 'unknown' || cardId === undefined) {
        if (event && event.target) {
            const button = event.target.closest('button');
            const cardElement = button?.closest('[data-card-id]');
            cardId = cardElement?.dataset?.cardId;
            console.log('ID retrieved from DOM:', cardId);
        }

        if (!cardId || cardId === 'undefined' || cardId === 'unknown') {
            console.error('Invalid card ID:', cardId);
            showNotification(t('invalid_card_id'), 'error');
            return;
        }
    }

    // If it's a temporary ID, do only visual flip
    if (cardId.toString().startsWith('temp-')) {
        console.log('Temporary ID detected, local flip only:', cardId);
    }

    // Find card in DOM
    const cardElement = document.querySelector(`[data-card-id="${cardId}"]`);
    const frontElement = cardElement?.querySelector('.card-front-text');
    const backElement = cardElement?.querySelector('.card-back-text');

    if (!cardElement || !frontElement || !backElement) {
        console.error('Card elements not found for ID:', cardId);
        showNotification(t('card_elements_not_found'), 'error');
        return;
    }

    // Add loading animation on the button
    const button = cardElement.querySelector('button[title="Inverser recto/verso"]');

    if (!button) {
        console.error('Flip button not found for card:', cardId);
        showNotification(t('flip_button_not_found'), 'error');
        return;
    }

    const originalContent = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="spinner-border spinner-border-sm"></i>';

    try {
        let apiSuccess = true;

        // For temporary IDs, do only visual flip
        if (cardId.toString().startsWith('temp-')) {
            console.log('Local flip for temporary ID');
            // Simulate API delay for UX
            await new Promise(resolve => setTimeout(resolve, 200));
        } else {
            // For real cards, call API
            const response = await fetch(`/api/v1/revision/api/flashcards/${cardId}/flip_card/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            apiSuccess = response.ok && data.success;

            if (!apiSuccess) {
                console.error('API flip error:', data);
                showNotification(data.error || t('flip_error'), 'error');
                return;
            }
        }

        if (apiSuccess) {
            // Flip animation - swap content
            const frontText = frontElement.textContent;
            const backText = backElement.textContent;

            // Fade out animation
            cardElement.style.transition = 'opacity 0.2s ease';
            cardElement.style.opacity = '0.5';

            setTimeout(() => {
                // Swap content
                frontElement.textContent = backText;
                backElement.textContent = frontText;

                // Fade in animation
                cardElement.style.opacity = '1';

                const message = cardId.toString().startsWith('temp-') ?
                    t('card_flipped_temp') : t('card_flipped');
                showNotification(message, 'success');
            }, 200);
        }
    } catch (error) {
        showNotification(t('network_error'), 'error');
        console.error(error);
    } finally {
        // Restore button
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalContent;
        }, 400);
    }
};

// ==================== Expose Functions Globally ====================
window.translateText = translateText;

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Translation script loaded');

    // Keyboard shortcuts for translation
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + Shift + T to translate front to back
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
            event.preventDefault();
            const frontTextarea = document.getElementById('newCardFront');
            if (frontTextarea && frontTextarea.value.trim()) {
                translateText('front');
            }
        }

        // Ctrl/Cmd + Shift + R to translate back to front
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'R') {
            event.preventDefault();
            const backTextarea = document.getElementById('newCardBack');
            if (backTextarea && backTextarea.value.trim()) {
                translateText('back');
            }
        }
    });
});
