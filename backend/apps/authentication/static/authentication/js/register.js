document.addEventListener('DOMContentLoaded', function() {
    const usernameField = document.querySelector('input[name="username"]');
    const passwordField = document.querySelector('input[name="password1"]');
    const confirmPasswordField = document.querySelector('input[name="password2"]');
    const nativeLanguageField = document.querySelector('select[name="native_language"]');
    const targetLanguageField = document.querySelector('select[name="target_language"]');
    
    // Username validation
    if (usernameField) {
        console.log('Username field found, setting up validation');
        let usernameTimeout;
        
        usernameField.addEventListener('input', function() {
            const username = this.value.trim();
            console.log('Username input changed:', username);
            clearTimeout(usernameTimeout);
            
            // Remove any existing feedback
            const existingFeedback = this.parentElement.querySelector('.username-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            if (username.length < 3) {
                if (username.length > 0) {
                    console.log('Username too short, showing error');
                    showUsernameFeedback(this, 'Le nom d\'utilisateur doit contenir au moins 3 caractères', 'error');
                }
                return;
            }
            
            // Vérifier que le username contient au moins une lettre ou un chiffre
            const hasAlphaNumeric = /[a-zA-Z0-9]/.test(username);
            if (!hasAlphaNumeric) {
                console.log('Username has no alphanumeric characters, showing error');
                showUsernameFeedback(this, 'Le nom d\'utilisateur doit contenir au moins une lettre ou un chiffre', 'error');
                this.setCustomValidity('Le nom d\'utilisateur doit contenir au moins une lettre ou un chiffre');
                return;
            } else {
                this.setCustomValidity('');
            }
            
            // Debounce the API call
            console.log('Starting debounced username check');
            usernameTimeout = setTimeout(() => {
                console.log('Checking username availability:', username);
                checkUsernameAvailability(username, this);
            }, 500);
        });
    } else {
        console.log('Username field not found!');
    }
    
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            const password = this.value;
            const strengthBar = document.getElementById('strengthBar');
            const strengthText = document.getElementById('strengthText');
            
            if (!strengthBar || !strengthText) return;
            
            let strength = 0;
            let message = '';
            
            if (password.length >= 8) strength += 1;
            if (password.match(/[a-z]/)) strength += 1;
            if (password.match(/[A-Z]/)) strength += 1;
            if (password.match(/[0-9]/)) strength += 1;
            if (password.match(/[^a-zA-Z0-9]/)) strength += 1;
            
            switch (strength) {
                case 0:
                case 1:
                    strengthBar.style.width = '20%';
                    strengthBar.style.background = '#ef4444';
                    message = 'Très faible';
                    break;
                case 2:
                    strengthBar.style.width = '40%';
                    strengthBar.style.background = '#f97316';
                    message = 'Faible';
                    break;
                case 3:
                    strengthBar.style.width = '60%';
                    strengthBar.style.background = '#eab308';
                    message = 'Moyen';
                    break;
                case 4:
                    strengthBar.style.width = '80%';
                    strengthBar.style.background = '#22c55e';
                    message = 'Fort';
                    break;
                case 5:
                    strengthBar.style.width = '100%';
                    strengthBar.style.background = '#16a34a';
                    message = 'Très fort';
                    break;
            }
            
            strengthText.textContent = message;
        });
    }
    
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            const password1 = document.querySelector('input[name="password1"]').value;
            const password2 = this.value;
            
            if (password2 && password1 !== password2) {
                this.setCustomValidity('Les mots de passe ne correspondent pas');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Language validation
    function validateLanguageSelection() {
        if (!nativeLanguageField || !targetLanguageField) return;
        
        const nativeLanguage = nativeLanguageField.value;
        const targetLanguage = targetLanguageField.value;
        
        // Remove any existing feedback
        const existingFeedback = document.querySelector('.language-validation-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Check if both languages are selected and identical
        if (nativeLanguage && targetLanguage && nativeLanguage === targetLanguage) {
            // Show error message
            const feedback = document.createElement('div');
            feedback.className = 'language-validation-feedback error-message';
            feedback.innerHTML = '<i class="bi bi-exclamation-circle"></i> La langue native et la langue cible ne peuvent pas être identiques.';
            
            // Insert after target language field
            const targetLanguageGroup = targetLanguageField.closest('.form-group');
            if (targetLanguageGroup) {
                targetLanguageGroup.appendChild(feedback);
            }
            
            // Set custom validity to prevent form submission
            nativeLanguageField.setCustomValidity('Les langues ne peuvent pas être identiques');
            targetLanguageField.setCustomValidity('Les langues ne peuvent pas être identiques');
            
            return false;
        } else {
            // Clear custom validity if languages are different
            nativeLanguageField.setCustomValidity('');
            targetLanguageField.setCustomValidity('');
            return true;
        }
    }
    
    // Add event listeners for language validation
    if (nativeLanguageField) {
        nativeLanguageField.addEventListener('change', validateLanguageSelection);
    }
    
    if (targetLanguageField) {
        targetLanguageField.addEventListener('change', validateLanguageSelection);
    }
});

// Helper functions for username validation
function showUsernameFeedback(input, message, type) {
    console.log('Creating feedback:', { message, type });
    const feedback = document.createElement('div');
    feedback.className = `username-feedback ${type}`;
    
    let iconClass;
    if (type === 'success') {
        iconClass = 'bi-check-circle';
    } else if (type === 'error') {
        iconClass = 'bi-exclamation-circle';
    } else if (type === 'loading') {
        iconClass = 'bi-clock';
    }
    
    feedback.innerHTML = `<i class="bi ${iconClass}"></i> ${message}`;
    
    // Insert after the form-text div
    const formText = input.parentElement.querySelector('.form-text');
    console.log('Form text element found:', formText);
    if (formText) {
        formText.insertAdjacentElement('afterend', feedback);
        console.log('Inserted feedback after form-text');
    } else {
        input.insertAdjacentElement('afterend', feedback);
        console.log('Inserted feedback after input');
    }
}

async function checkUsernameAvailability(username, input) {
    try {
        // Show loading state
        console.log('Showing loading feedback');
        showUsernameFeedback(input, 'Vérification en cours...', 'loading');
        
        const csrfToken = getCsrfToken();
        console.log('CSRF Token:', csrfToken);
        
        const url = `/api/check-username/?username=${encodeURIComponent(username)}`;
        console.log('Making request to:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // Remove loading feedback
        const loadingFeedback = input.parentElement.querySelector('.username-feedback');
        if (loadingFeedback) {
            loadingFeedback.remove();
        }
        
        if (data.available) {
            console.log('Username available, showing success');
            showUsernameFeedback(input, data.message, 'success');
            input.setCustomValidity('');
        } else {
            console.log('Username not available, showing error');
            showUsernameFeedback(input, data.message, 'error');
            input.setCustomValidity(data.message);
        }
    } catch (error) {
        console.error('Username check error:', error);
        const loadingFeedback = input.parentElement.querySelector('.username-feedback');
        if (loadingFeedback) {
            loadingFeedback.remove();
        }
        showUsernameFeedback(input, 'Erreur lors de la vérification', 'error');
    }
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    // Try to get from meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Try to get from input field
    const inputField = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (inputField) {
        return inputField.value;
    }
    
    return '';
}