/**
 * Todo Settings JavaScript
 * Handles todo-specific settings functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('[TodoSettings] Loading todo settings JavaScript...');
    
    // Initialize todo settings if on settings page
    if (document.querySelector('#todo')) {
        initTodoSettings();
    }
});

function initTodoSettings() {
    console.log('[TodoSettings] Initializing todo settings...');
    
    // Setup form handlers
    setupTodoFormHandlers();
    
    // Setup range sliders
    setupRangeSliders();
    
    // Setup section toggles
    setupSectionToggles();
    
    // Load initial data
    loadTodoSettingsData();
}

function setupTodoFormHandlers() {
    const forms = document.querySelectorAll('#todo form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            saveTodoSettings(this);
        });
    });
}

function setupRangeSliders() {
    const rangeInputs = document.querySelectorAll('#todo .range-input input[type="range"]');
    
    rangeInputs.forEach(slider => {
        // Update display value on input
        slider.addEventListener('input', function() {
            updateRangeValue(this);
        });
        
        // Initialize current value
        updateRangeValue(slider);
    });
}

function updateRangeValue(slider) {
    const valueSpan = slider.parentElement.querySelector('.range-value');
    if (!valueSpan) return;
    
    const value = parseInt(slider.value);
    
    // Format special values
    if (slider.name === 'reminder_minutes_before' && value >= 60) {
        const hours = Math.floor(value / 60);
        const minutes = value % 60;
        valueSpan.textContent = hours + 'h' + (minutes > 0 ? minutes + 'm' : '');
    } else if (slider.name === 'auto_archive_days') {
        valueSpan.textContent = value + ' jours';
    } else {
        valueSpan.textContent = value;
    }
}

function setupSectionToggles() {
    const toggles = document.querySelectorAll('#todo .section-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const section = this.closest('.content-section');
            const content = section.querySelector('.section-content');
            const icon = this.querySelector('i');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.classList.remove('bi-chevron-down');
                icon.classList.add('bi-chevron-up');
            } else {
                content.style.display = 'none';
                icon.classList.remove('bi-chevron-up');
                icon.classList.add('bi-chevron-down');
            }
        });
    });
}

async function loadTodoSettingsData() {
    console.log('[TodoSettings] Loading current todo settings...');
    
    try {
        const response = await fetch('/api/v1/todo/settings/');
        
        if (response.ok) {
            const data = await response.json();
            console.log('[TodoSettings] Settings loaded:', data);
            populateTodoSettings(data);
        } else {
            console.warn('[TodoSettings] Could not load settings:', response.status);
        }
    } catch (error) {
        console.error('[TodoSettings] Error loading settings:', error);
    }
}

function populateTodoSettings(settings) {
    console.log('[TodoSettings] Populating form fields with settings...');
    
    // Iterate through all setting fields
    Object.entries(settings).forEach(([key, value]) => {
        const field = document.querySelector(`#todo [name="${key}"]`);
        
        if (field) {
            if (field.type === 'checkbox') {
                field.checked = value;
            } else if (field.type === 'range') {
                field.value = value;
                updateRangeValue(field);
            } else {
                field.value = value;
            }
        }
    });
}

async function saveTodoSettings(form) {
    console.log('[TodoSettings] Saving todo settings...');
    
    const formData = new FormData(form);
    const settings = {};
    
    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
        if (key !== 'csrfmiddlewaretoken' && key !== 'setting_type') {
            // Handle checkboxes (they only appear in FormData when checked)
            const field = form.querySelector(`[name="${key}"]`);
            if (field && field.type === 'checkbox') {
                settings[key] = true;
            } else {
                settings[key] = value;
            }
        }
    }
    
    // Add unchecked checkboxes as false
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        if (!formData.has(checkbox.name)) {
            settings[checkbox.name] = false;
        }
    });
    
    console.log('[TodoSettings] Settings to save:', settings);
    
    try {
        const response = await fetch('/api/v1/todo/settings/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('[TodoSettings] Settings saved successfully:', result);
            showSaveSuccess(form);
        } else {
            console.error('[TodoSettings] Error saving settings:', response.status);
            showSaveError(form);
        }
    } catch (error) {
        console.error('[TodoSettings] Error saving settings:', error);
        showSaveError(form);
    }
}

function showSaveSuccess(form) {
    const button = form.querySelector('button[type="submit"]');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="bi bi-check"></i> Enregistré !';
    button.style.backgroundColor = '#28a745';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.backgroundColor = '';
    }, 2000);
}

function showSaveError(form) {
    const button = form.querySelector('button[type="submit"]');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Erreur';
    button.style.backgroundColor = '#dc3545';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.backgroundColor = '';
    }, 2000);
}

// Global functions for statistics
async function loadTodoStats() {
    console.log('[TodoSettings] Loading todo statistics...');
    
    try {
        const response = await fetch('/api/v1/todo/dashboard/');
        
        if (response.ok) {
            const data = await response.json();
            console.log('[TodoSettings] Statistics loaded:', data);
            
            const stats = data.stats || {};
            updateStatElement('total-tasks', stats.total_tasks || 0);
            updateStatElement('completed-tasks', stats.completed_tasks || 0);
            updateStatElement('active-projects', stats.active_projects || 0);
            updateStatElement('completion-rate', (stats.completion_rate || 0) + '%');
        } else {
            console.error('[TodoSettings] Error loading statistics:', response.status);
            setFallbackStats();
        }
    } catch (error) {
        console.error('[TodoSettings] Error loading statistics:', error);
        setFallbackStats();
    }
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function setFallbackStats() {
    updateStatElement('total-tasks', '0');
    updateStatElement('completed-tasks', '0');
    updateStatElement('active-projects', '0');
    updateStatElement('completion-rate', '0%');
}

async function testTodoAPI() {
    console.log('[TodoSettings] Testing todo API...');
    
    try {
        const response = await fetch('/api/v1/todo/settings/');
        
        if (response.ok) {
            const data = await response.json();
            console.log('[TodoSettings] API test successful:', data);
            alert(`Test API Todo réussi !\nThème: ${data.theme || 'auto'}\nMode compact: ${data.compact_mode ? 'Oui' : 'Non'}`);
        } else {
            console.error('[TodoSettings] API test failed:', response.status);
            alert('Test API échoué - Status: ' + response.status);
        }
    } catch (error) {
        console.error('[TodoSettings] API test error:', error);
        alert('Test API échoué: ' + error.message);
    }
}

// Make functions globally available
window.loadTodoStats = loadTodoStats;
window.testTodoAPI = testTodoAPI;

console.log('[TodoSettings] Todo settings JavaScript loaded successfully');