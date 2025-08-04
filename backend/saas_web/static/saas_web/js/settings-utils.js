/**
 * Settings Utilities
 * Shared utility functions for all settings pages
 */

// CSRF Token handling
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.cookie.match(/csrftoken=([^;]+)/)?.[1];
}

// Temporary message display
function showTemporaryMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Form validation utilities
function getOrCreateFeedback(input, id) {
    let feedback = document.getElementById(id);
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.id = id;
        feedback.className = 'form-feedback';
        feedback.style.fontSize = '12px';
        feedback.style.marginTop = '4px';
        input.parentNode.appendChild(feedback);
    }
    return feedback;
}

function showFieldError(input, feedback, message) {
    input.classList.remove('is-valid', 'is-pending');
    input.classList.add('is-invalid');
    feedback.textContent = message;
    feedback.style.color = '#dc3545';
}

function showFieldSuccess(input, feedback, message) {
    input.classList.remove('is-invalid', 'is-pending');
    input.classList.add('is-valid');
    feedback.textContent = message;
    feedback.style.color = '#198754';
}

function showFieldPending(input, feedback, message) {
    input.classList.remove('is-invalid', 'is-valid');
    input.classList.add('is-pending');
    feedback.textContent = message;
    feedback.style.color = '#6c757d';
}

// Generic field validation
function setupFormValidation() {
    const inputs = document.querySelectorAll('input[required], input[type="email"], input[type="tel"]');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            validateField(input);
        });
        
        input.addEventListener('input', () => {
            if (input.classList.contains('is-invalid')) {
                validateField(input);
            }
        });
    });
}

function validateField(input) {
    const value = input.value.trim();
    let isValid = true;
    let message = '';
    
    // Required field validation
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        message = 'Ce champ est requis';
    }
    
    // Email validation
    if (input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Format d\'email invalide';
        }
    }
    
    // Phone validation
    if (input.type === 'tel' && value) {
        const phoneRegex = /^\+\d{1,3}\d{8,14}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            message = 'Format de téléphone invalide';
        }
    }
    
    // Update field appearance
    input.classList.remove('is-valid', 'is-invalid');
    input.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Update feedback message
    let feedback = input.parentNode.querySelector('.form-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'form-feedback';
        input.parentNode.appendChild(feedback);
    }
    
    feedback.textContent = message;
    feedback.className = `form-feedback ${isValid ? 'form-success' : 'form-error'}`;
}

// Generic form submission handler
async function handleFormSubmission(form) {
    // Skip forms without valid action or on app manager page
    if (!form.action || form.action.includes('app-manager')) {
        console.log('[Settings Utils] Skipping form submission for app manager or invalid action');
        return;
    }
    
    // Prevent multiple simultaneous submissions
    if (form.hasAttribute('data-submitting')) {
        console.log('[Settings Utils] Form already being submitted, ignoring');
        return;
    }
    
    form.setAttribute('data-submitting', 'true');
    
    try {
        showTemporaryMessage('Sauvegarde en cours...', 'info');
        
        const formData = new FormData(form);
        
        // Auto-detect setting type based on form fields (only if not already set)
        if (!formData.has('setting_type')) {
            if (formData.has('profile_picture')) {
                formData.append('setting_type', 'profile');
            } else if (form.querySelector('input[name="first_name"], input[name="last_name"], input[name="username"], input[name*="general"]')) {
                formData.append('setting_type', 'general');
            } else if (form.querySelector('input[name="bio"], input[name="phone_number"], input[name*="profile"]')) {
                formData.append('setting_type', 'profile');
            }
        }
        
        // Debug logging
        console.log('[Settings Utils] Form submission details:', {
            action: form.action,
            formData: Array.from(formData.entries()),
            hasProfilePicture: formData.has('profile_picture'),
            settingType: formData.get('setting_type')
        });
        
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        console.log('[Settings Utils] Response status:', response.status);
        
        let result;
        const responseText = await response.text();
        
        try {
            result = JSON.parse(responseText);
            console.log('[Settings Utils] Response data:', result);
        } catch (e) {
            console.error('[Settings Utils] Failed to parse JSON response:', responseText);
            throw new Error('Invalid JSON response');
        }
        
        if (result.success) {
            showTemporaryMessage(result.message || 'Paramètres sauvegardés', 'success');
            
            // Handle profile picture update if function exists
            if (result.profile_picture_url && window.updateAllProfilePictures) {
                window.updateAllProfilePictures(result.profile_picture_url);
            }
            
            return result;
        } else {
            showTemporaryMessage(result.message || 'Erreur lors de la sauvegarde', 'error');
            return null;
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showTemporaryMessage('Erreur de connexion', 'error');
        return null;
    } finally {
        // Always remove the submitting flag
        form.removeAttribute('data-submitting');
    }
}

// Theme preview functionality
function setupThemePreview() {
    const themeOptions = document.querySelectorAll('.theme-option');
    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            const theme = option.getAttribute('data-theme');
            previewTheme(theme);
            
            // Update selection
            themeOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
        });
    });
    
    const colorOptions = document.querySelectorAll('.color-option');
    colorOptions.forEach(option => {
        option.addEventListener('click', () => {
            const color = option.getAttribute('data-color');
            previewColor(color);
            
            // Update selection
            colorOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
        });
    });
}

function previewTheme(theme) {
    const body = document.body;
    body.classList.remove('theme-light', 'theme-dark', 'theme-auto');
    
    if (theme === 'dark') {
        body.classList.add('theme-dark');
    } else if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
    } else {
        body.classList.add('theme-light');
    }
}

function previewColor(color) {
    const root = document.documentElement;
    const colors = {
        violet: '#8b5cf6',
        blue: '#3b82f6',
        green: '#10b981',
        red: '#ef4444',
        orange: '#f59e0b'
    };
    
    if (colors[color]) {
        root.style.setProperty('--accent-color', colors[color]);
    }
}

// Section collapse functionality
function setupSectionCollapse() {
    const sectionToggles = document.querySelectorAll('.section-toggle');
    sectionToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const section = toggle.closest('.content-section');
            const content = section.querySelector('.section-content');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                toggle.innerHTML = '<i class="bi bi-chevron-up"></i>';
            } else {
                content.classList.add('collapsed');
                toggle.innerHTML = '<i class="bi bi-chevron-down"></i>';
            }
        });
    });
}

// Initialize utilities when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Settings Utils] Initializing utilities...');
    
    setupFormValidation();
    setupThemePreview();
    setupSectionCollapse();
    
    // Setup generic form submissions
    document.querySelectorAll('form').forEach(form => {
        // Skip forms that have specific handlers or already have our handler
        if (!form.hasAttribute('data-custom-handler') && !form.hasAttribute('data-utils-handled')) {
            form.setAttribute('data-utils-handled', 'true');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await handleFormSubmission(form);
            });
        }
    });
    
    console.log('[Settings Utils] Utilities initialized successfully');
});

// Export utilities for use in other scripts
window.settingsUtils = {
    getCsrfToken,
    showTemporaryMessage,
    getOrCreateFeedback,
    showFieldError,
    showFieldSuccess,
    showFieldPending,
    validateField,
    handleFormSubmission,
    previewTheme,
    previewColor
};