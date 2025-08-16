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
        option.addEventListener('click', () => {
            const backgroundValue = option.dataset.background;
            
            // Update UI
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
            showTemporaryMessage('Arrière-plan du dashboard modifié avec succès', 'success');
        });
    });
}

function setDashboardBackground(backgroundValue) {
    const backgroundColors = {
        'default': '#f8fafc',
        'white': '#ffffff',
        'gray': '#f3f4f6',
        'dark': '#1f2937',
        'blue': '#eff6ff',
        'green': '#f0fdf4',
        'purple': '#faf5ff'
    };
    
    const color = backgroundColors[backgroundValue] || backgroundColors['default'];
    document.body.style.background = color;
    
    // Also apply to dashboard content area if it exists
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        contentArea.style.background = 'transparent';
    }
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