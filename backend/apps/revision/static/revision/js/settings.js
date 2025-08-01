/**
 * Revision Settings JavaScript
 * Handles form interactions and auto-save for revision settings
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Revision Settings] Initializing revision settings JavaScript');
    
    // Initialize revision settings functionality
    initRevisionSettings();
});

function initRevisionSettings() {
    // Handle form submissions with better UX
    setupFormHandlers();
    
    // Handle preset buttons
    setupPresetButtons();
    
    // Handle range sliders
    setupRangeSliders();
    
    // Handle stats tabs
    setupStatsTabs();
    
    // Load word stats if enabled
    loadWordStatsIfEnabled();
}

function setupFormHandlers() {
    const forms = document.querySelectorAll('#revision form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(form);
        });
    });
}

async function handleFormSubmission(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sauvegarde...';
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(form);
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         document.cookie.match(/csrftoken=([^;]+)/)?.[1];
        
        const response = await fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Success feedback
            submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Sauvegardé';
            submitBtn.classList.remove('btn-primary');
            submitBtn.classList.add('btn-success');
            
            console.log('[Revision Settings] Form saved successfully:', result);
            
            // Show temporary success message
            showTemporaryMessage('Paramètres sauvegardés avec succès', 'success');
        } else {
            throw new Error(result.message || 'Erreur de sauvegarde');
        }
    } catch (error) {
        console.error('[Revision Settings] Form submission error:', error);
        
        // Error feedback
        submitBtn.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Erreur';
        submitBtn.classList.remove('btn-primary');
        submitBtn.classList.add('btn-danger');
        
        showTemporaryMessage('Erreur lors de la sauvegarde', 'error');
    } finally {
        // Reset button after 2 seconds
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.classList.remove('btn-success', 'btn-danger');
            submitBtn.classList.add('btn-primary');
            submitBtn.disabled = false;
        }, 2000);
    }
}

function setupPresetButtons() {
    const presetButtons = document.querySelectorAll('.preset-btn');
    
    presetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const preset = this.dataset.preset;
            applyRevisionPreset(preset);
        });
    });
}

function applyRevisionPreset(presetName) {
    console.log(`[Revision Settings] Applying preset: ${presetName}`);
    
    // Mark preset as active
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-preset="${presetName}"]`).classList.add('active');
    
    // Apply preset values
    const presets = {
        beginner: { cards_per_session: 10, default_session_duration: 15 },
        intermediate: { cards_per_session: 20, default_session_duration: 20 },
        advanced: { cards_per_session: 30, default_session_duration: 30 },
        intensive: { cards_per_session: 50, default_session_duration: 45 }
    };
    
    if (presets[presetName]) {
        const settings = presets[presetName];
        const cardsSlider = document.querySelector('[name="cards_per_session"]');
        const durationSlider = document.querySelector('[name="default_session_duration"]');
        
        if (cardsSlider) {
            cardsSlider.value = settings.cards_per_session;
            cardsSlider.parentElement.querySelector('.range-value').textContent = settings.cards_per_session;
        }
        
        if (durationSlider) {
            durationSlider.value = settings.default_session_duration;
            durationSlider.parentElement.querySelector('.range-value').textContent = settings.default_session_duration;
        }
    }
}

function setupRangeSliders() {
    const sliders = document.querySelectorAll('.range-input input[type="range"]');
    
    sliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const valueSpan = this.parentElement.querySelector('.range-value');
            if (valueSpan) {
                valueSpan.textContent = this.value;
            }
        });
    });
}

function setupStatsTabs() {
    const statsTabs = document.querySelectorAll('.stats-tab');
    
    statsTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            switchStatsTab(tabId);
        });
    });
}

function switchStatsTab(tabId) {
    // Update tab active states
    document.querySelectorAll('.stats-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

    // Update content active states
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    const targetPane = document.getElementById(tabId === 'known' ? 'known-words' : 
                                             tabId === 'to-learn' ? 'to-learn-words' : 'summary-stats');
    if (targetPane) {
        targetPane.classList.add('active');
    }

    // Load data for the selected tab
    loadWordStats(tabId);
}

function loadWordStatsIfEnabled() {
    const showWordStats = document.querySelector('[name="show_word_stats"]');
    if (showWordStats && showWordStats.checked) {
        loadWordStats('known');
    }
}

async function loadWordStats(type) {
    console.log(`[Revision Settings] Loading ${type} word statistics`);
    
    const apiUrl = '/api/revision/word-stats/';
    const params = new URLSearchParams();
    
    if (type === 'known') {
        params.append('type', 'known');
    } else if (type === 'to-learn') {
        params.append('type', 'to_learn');
    } else {
        params.append('type', 'all');
    }

    try {
        const response = await fetch(`${apiUrl}?${params.toString()}`);
        const data = await response.json();
        displayWordStats(type, data);
    } catch (error) {
        console.error(`[Revision Settings] Error loading ${type} stats:`, error);
        showStatsError(type);
    }
}

function displayWordStats(type, data) {
    const container = document.getElementById(
        type === 'known' ? 'known-words' : 
        type === 'to-learn' ? 'to-learn-words' : 'summary-stats'
    );

    if (!container) return;

    if (type === 'summary' || type === 'all') {
        // Display summary statistics
        container.innerHTML = `
            <div class="stats-summary">
                <div class="summary-card">
                    <div class="summary-number">${data.statistics?.total_known || 0}</div>
                    <div class="summary-label">Mots connus</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${data.statistics?.total_to_learn || 0}</div>
                    <div class="summary-label">À apprendre</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${data.statistics?.total_words || 0}</div>
                    <div class="summary-label">Total</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${data.statistics?.completion_rate || 0}%</div>
                    <div class="summary-label">Taux de réussite</div>
                </div>
            </div>
        `;
    } else {
        // Display word lists
        const words = type === 'known' ? data.known_words : data.words_to_learn;
        
        if (!words || words.length === 0) {
            container.innerHTML = `
                <div class="loading-spinner">
                    Aucun mot ${type === 'known' ? 'connu' : 'à apprendre'} trouvé.
                </div>
            `;
            return;
        }

        const wordsHtml = words.map(word => `
            <div class="word-item">
                <div class="word-content">
                    <div class="word-front">${word.front_text}</div>
                    <div class="word-back">${word.back_text}</div>
                </div>
                <div class="word-meta">
                    <div class="word-deck">${word.deck_name}</div>
                    ${type === 'to-learn' ? `
                        <div class="word-progress">${word.correct_reviews}/${word.reviews_needed + word.correct_reviews}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${word.progress_percentage}%"></div>
                        </div>
                    ` : `
                        <div class="word-progress">Appris ✓</div>
                    `}
                </div>
            </div>
        `).join('');

        container.innerHTML = wordsHtml;
    }
}

function showStatsError(type) {
    const container = document.getElementById(
        type === 'known' ? 'known-words' : 
        type === 'to-learn' ? 'to-learn-words' : 'summary-stats'
    );
    
    if (container) {
        container.innerHTML = `
            <div class="loading-spinner" style="color: #dc3545;">
                Erreur lors du chargement des statistiques.
            </div>
        `;
    }
}

function showTemporaryMessage(message, type = 'info') {
    // Create or get existing message container
    let messageContainer = document.querySelector('.revision-message');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.className = 'revision-message';
        document.body.appendChild(messageContainer);
    }
    
    // Set message content and type
    messageContainer.textContent = message;
    messageContainer.className = `revision-message ${type} show`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        messageContainer.classList.remove('show');
    }, 3000);
}

// Add CSS for message container
const messageStyles = `
.revision-message {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 16px;
    border-radius: 8px;
    font-weight: 500;
    z-index: 1000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
}

.revision-message.show {
    transform: translateX(0);
}

.revision-message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.revision-message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.revision-message.info {
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = messageStyles;
document.head.appendChild(styleSheet);