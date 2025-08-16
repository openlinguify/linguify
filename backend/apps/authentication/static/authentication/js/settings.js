/**
 * Authentication Settings JavaScript
 * Handles profile, account management, and authentication-specific settings
 */

// Profile picture handling
function validateProfilePicture(event) {
    const input = event.target;
    const file = input.files[0];
    const feedback = getOrCreateFeedback(input, 'picture-feedback');
    
    if (!file) {
        feedback.textContent = '';
        input.classList.remove('is-invalid', 'is-valid');
        resetProfilePicturePreview();
        return;
    }
    
    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showFieldError(input, feedback, 'Format non supporté. Utilisez JPG, PNG ou WEBP');
        resetProfilePicturePreview();
        return;
    }
    
    // Check file size (5MB max)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        showFieldError(input, feedback, 'Fichier trop volumineux. Maximum 5MB');
        resetProfilePicturePreview();
        return;
    }
    
    showFieldSuccess(input, feedback, `Image valide (${(file.size / 1024 / 1024).toFixed(1)}MB)`);
    previewProfilePicture(file);
}

function previewProfilePicture(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const avatars = document.querySelectorAll('.user-avatar img');
        avatars.forEach(avatar => {
            avatar.src = e.target.result;
        });
    };
    reader.readAsDataURL(file);
}

function resetProfilePicturePreview() {
    const avatars = document.querySelectorAll('.user-avatar img');
    avatars.forEach(avatar => {
        const originalSrc = avatar.getAttribute('data-original-src');
        if (originalSrc) {
            avatar.src = originalSrc;
        }
    });
}

function updateAllProfilePictures(newUrl) {
    const avatars = document.querySelectorAll('.user-avatar img');
    avatars.forEach(avatar => {
        avatar.src = newUrl;
        avatar.setAttribute('data-original-src', newUrl);
    });
}

// Account management functions
async function suspendAccount() {
    if (confirm('Êtes-vous sûr de vouloir suspendre temporairement votre compte ? Vous pourrez le réactiver à tout moment.')) {
        try {
            showTemporaryMessage('Suspension du compte en cours...', 'info');
            
            const response = await fetch('/auth/api/suspend-account/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showTemporaryMessage('Compte suspendu avec succès. Vous allez être déconnecté.', 'success');
                setTimeout(() => {
                    window.location.href = '/auth/logout/';
                }, 2000);
            } else {
                showTemporaryMessage('Erreur lors de la suspension: ' + (result.error || 'Erreur inconnue'), 'error');
            }
        } catch (error) {
            console.error('Suspension error:', error);
            showTemporaryMessage('Erreur de connexion lors de la suspension', 'error');
        }
    }
}

async function exportData() {
    if (confirm('Souhaitez-vous exporter toutes vos données personnelles ?')) {
        try {
            showTemporaryMessage('Export des données en cours...', 'info');
            
            const response = await fetch('/auth/api/export-data/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showTemporaryMessage('Export demandé avec succès ! Vous recevrez un email avec vos données dans quelques minutes.', 'success');
                
                if (result.download_url) {
                    const link = document.createElement('a');
                    link.href = result.download_url;
                    link.download = `linguify_data_export_${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            } else {
                showTemporaryMessage('Erreur lors de l\'export: ' + (result.error || 'Erreur inconnue'), 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            showTemporaryMessage('Erreur de connexion lors de l\'export', 'error');
        }
    }
}

async function deleteAccount() {
    const confirmText = 'SUPPRIMER';
    const userInput = prompt(
        `⚠️ ATTENTION : Cette action est irréversible !\n\n` +
        `Toutes vos données seront définitivement supprimées :\n` +
        `• Profil utilisateur\n` +
        `• Progression d'apprentissage\n` +
        `• Notes et flashcards\n` +
        `• Historique d'activité\n\n` +
        `Pour confirmer, tapez exactement : ${confirmText}`
    );
    
    if (userInput === confirmText) {
        if (confirm('Dernière confirmation : êtes-vous absolument certain de vouloir supprimer votre compte ?')) {
            try {
                showTemporaryMessage('Suppression du compte en cours...', 'warning');
                
                const response = await fetch('/auth/api/delete-account/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        confirmation: confirmText,
                        immediate: false
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(
                        `Votre compte a été programmé pour suppression.\n\n` +
                        `• Date de suppression : ${new Date(result.deletion_date).toLocaleDateString('fr-FR')}\n` +
                        `• Vous avez ${result.days_remaining} jours pour annuler\n` +
                        `• Un email de confirmation vous a été envoyé\n\n` +
                        `Vous pouvez annuler cette suppression en vous reconnectant avant la date limite.`
                    );
                    
                    setTimeout(() => {
                        window.location.href = '/auth/logout/';
                    }, 3000);
                } else {
                    showTemporaryMessage('Erreur lors de la suppression: ' + (result.error || 'Erreur inconnue'), 'error');
                }
            } catch (error) {
                console.error('Account deletion error:', error);
                showTemporaryMessage('Erreur de connexion lors de la suppression', 'error');
            }
        }
    } else if (userInput !== null) {
        alert('Texte de confirmation incorrect. Suppression annulée.');
    }
}

// Ripple effect for better UX
function createRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: radial-gradient(circle, rgba(45, 91, 186, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
        z-index: 1;
    `;
    
    // Add keyframes for ripple animation if not already added
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    element.appendChild(ripple);
    
    // Remove ripple after animation
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
        }
    }, 600);
}

// Dashboard background handling
function initDashboardBackgroundOptions() {
    const backgroundOptions = document.querySelectorAll('.background-option');
    const hiddenInput = document.getElementById('dashboard-background-input');
    
    // Load saved background from localStorage or default
    const savedBackground = localStorage.getItem('dashboard_background') || 'default';
    setDashboardBackground(savedBackground);
    
    // Set active option based on saved value
    backgroundOptions.forEach(option => {
        option.classList.remove('active');
        if (option.dataset.background === savedBackground) {
            option.classList.add('active');
        }
    });
    
    // Add click handlers
    backgroundOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            const backgroundValue = option.dataset.background;
            
            // Create ripple effect
            createRippleEffect(e, option);
            
            // Update UI with slight delay for ripple effect
            setTimeout(() => {
                backgroundOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                
                // Update hidden input
                if (hiddenInput) {
                    hiddenInput.value = backgroundValue;
                }
                
                // Apply background immediately
                setDashboardBackground(backgroundValue);
                
                // Save to localStorage
                localStorage.setItem('dashboard_background', backgroundValue);
                
                // Show success message
                if (typeof showTemporaryMessage === 'function') {
                    showTemporaryMessage('Arrière-plan modifié avec succès! 🎨', 'success');
                }
            }, 150);
        });
    });
}

function setDashboardBackground(backgroundValue) {
    const backgroundColors = {
        // Couleurs neutres
        'default': '#f8fafc',
        'white': '#ffffff',
        'gray-light': '#f9fafb',
        'gray': '#f3f4f6',
        
        // Couleurs Linguify
        'linguify-light': 'linear-gradient(135deg, #f0f4ff 0%, #e0f2fe 100%)',
        'linguify-accent': 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
        'linguify-purple': 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
        
        // Couleurs premium
        'warm': 'linear-gradient(135deg, #fefbf3 0%, #fef7ed 100%)',
        'cool': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        'nature': 'linear-gradient(135deg, #f7fee7 0%, #ecfccb 100%)',
        
        // Mode sombre
        'dark': '#1f2937',
        'dark-blue': 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        
        // Compatibilité ancienne version
        'blue': '#eff6ff',
        'green': '#f0fdf4',
        'purple': '#faf5ff'
    };
    
    const color = backgroundColors[backgroundValue] || backgroundColors['default'];
    document.body.style.setProperty('background', color, 'important');
    
    // Also apply to dashboard content area if it exists
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        contentArea.style.background = 'transparent';
    }
    
    // Remove all background classes first
    document.body.classList.remove(
        'bg-default', 'bg-white', 'bg-gray-light', 'bg-gray',
        'bg-linguify-light', 'bg-linguify-accent', 'bg-linguify-purple',
        'bg-warm', 'bg-cool', 'bg-nature', 
        'bg-dark', 'bg-dark-blue',
        'bg-blue', 'bg-green', 'bg-purple', // compatibility
        'dark-background' // old class
    );
    
    // Apply specific background class for automatic text color adaptation
    document.body.classList.add('bg-' + backgroundValue);
}

// Initialize authentication settings
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Authentication Settings] Initializing...');
    
    // Setup profile picture validation
    const profilePictureInput = document.querySelector('input[name="profile_picture"]');
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', validateProfilePicture);
    }
    
    // Setup dashboard background options
    initDashboardBackgroundOptions();
    
    console.log('[Authentication Settings] Initialized successfully');
});

// Make functions globally available
window.suspendAccount = suspendAccount;
window.exportData = exportData;
window.deleteAccount = deleteAccount;
window.validateProfilePicture = validateProfilePicture;