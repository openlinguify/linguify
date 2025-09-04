/**
 * Language Learning Settings JavaScript
 * Manages the settings interface for the Language Learning app
 */

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎓 Language Learning Settings JS loaded');
        
        // Initialize language learning settings
        initLanguageLearningSettings();
    });
    
    function initLanguageLearningSettings() {
        // Handle preset buttons
        const presetButtons = document.querySelectorAll('.preset-btn');
        presetButtons.forEach(button => {
            button.addEventListener('click', function() {
                const preset = this.dataset.preset;
                applyPreset(preset);
            });
        });
        
        // Handle form changes for auto-save
        const settingsForm = document.getElementById('language-learning-settings-form');
        if (settingsForm) {
            const inputs = settingsForm.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('change', function() {
                    saveSettings();
                });
            });
        }
        
        // Load statistics
        loadLanguageLearningStats();
        
        // Initialize range inputs
        initRangeInputs();
    }
    
    function applyPreset(presetName) {
        console.log(`Applying preset: ${presetName}`);
        
        const presets = {
            casual: {
                daily_goal_minutes: 10,
                weekly_goal_days: 3,
                preferred_difficulty: 'easy',
                reminder_enabled: false
            },
            regular: {
                daily_goal_minutes: 15,
                weekly_goal_days: 5,
                preferred_difficulty: 'normal',
                reminder_enabled: true
            },
            intensive: {
                daily_goal_minutes: 30,
                weekly_goal_days: 6,
                preferred_difficulty: 'hard',
                reminder_enabled: true
            },
            immersion: {
                daily_goal_minutes: 60,
                weekly_goal_days: 7,
                preferred_difficulty: 'hard',
                reminder_enabled: true
            }
        };
        
        const presetSettings = presets[presetName];
        if (presetSettings) {
            // Update form fields
            Object.keys(presetSettings).forEach(key => {
                const field = document.getElementById(key) || document.querySelector(`[name="${key}"]`);
                if (field) {
                    if (field.type === 'checkbox') {
                        field.checked = presetSettings[key];
                    } else {
                        field.value = presetSettings[key];
                    }
                    // Trigger change event
                    field.dispatchEvent(new Event('change'));
                }
            });
            
            // Show feedback
            showNotification(`Configuration "${presetName}" appliquée avec succès!`, 'success');
        }
    }
    
    function saveSettings() {
        const form = document.getElementById('language-learning-settings-form');
        if (!form) return;
        
        const formData = new FormData(form);
        
        // Show saving indicator
        showSavingIndicator();
        
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Paramètres sauvegardés automatiquement', 'success');
            } else {
                showNotification('Erreur lors de la sauvegarde: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            showNotification('Erreur lors de la sauvegarde', 'error');
        })
        .finally(() => {
            hideSavingIndicator();
        });
    }
    
    function loadLanguageLearningStats() {
        // Load stats via AJAX
        fetch('/language_learning/api/v1/items/stats/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatsDisplay(data.stats);
            }
        })
        .catch(error => {
            console.error('Stats loading error:', error);
        });
    }
    
    function updateStatsDisplay(stats) {
        // Update statistics in the UI
        const elements = {
            'total-languages': stats.total_languages || 0,
            'total-study-time': formatTime(stats.total_study_time || 0),
            'longest-streak': stats.longest_streak || 0,
            'lessons-completed': stats.total_lessons_completed || 0
        };
        
        Object.keys(elements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = elements[id];
            }
        });
    }
    
    function formatTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    }
    
    function initRangeInputs() {
        // Initialize range inputs with value display
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            const valueDisplay = input.parentElement.querySelector('.range-value');
            if (valueDisplay) {
                valueDisplay.textContent = input.value;
                input.addEventListener('input', function() {
                    valueDisplay.textContent = this.value;
                });
            }
        });
    }
    
    // Utility functions
    function showNotification(message, type = 'info') {
        // Use global notification service if available
        if (window.notificationService) {
            window.notificationService[type](message);
        } else {
            // Fallback notification
            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed top-0 end-0 m-3`;
            notification.style.zIndex = '9999';
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
    }
    
    function showSavingIndicator() {
        // Show saving indicator (you can customize this)
        const indicator = document.getElementById('saving-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }
    
    function hideSavingIndicator() {
        // Hide saving indicator
        const indicator = document.getElementById('saving-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || 
               '';
    }
    
    // Make functions available globally if needed
    window.languageLearningSettings = {
        applyPreset: applyPreset,
        saveSettings: saveSettings,
        loadStats: loadLanguageLearningStats
    };
    
})();