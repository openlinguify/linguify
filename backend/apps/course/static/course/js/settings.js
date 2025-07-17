/**
 * Course/Learning Settings JavaScript
 * Handles learning-specific settings functionality
 */

function initializeLearningSettings() {
    console.log('[Learning Settings] Initializing learning-specific settings...');
    
    // Learning objectives
    const objectivesSelect = document.querySelector('select[name="daily_learning_goal"]');
    if (objectivesSelect) {
        objectivesSelect.addEventListener('change', () => {
            const goal = objectivesSelect.value;
            const goalText = {
                '5': '5 minutes (Découverte)',
                '10': '10 minutes (Débutant)',
                '20': '20 minutes (Régulier)',
                '30': '30 minutes (Sérieux)',
                '60': '60 minutes (Intensif)'
            };
            showTemporaryMessage(`Objectif quotidien: ${goalText[goal]}`, 'info');
        });
    }
    
    // Language validation
    const nativeLanguageSelect = document.querySelector('select[name="native_language"]');
    const targetLanguageSelect = document.querySelector('select[name="target_language"]');
    
    if (nativeLanguageSelect && targetLanguageSelect) {
        function validateLanguages() {
            if (nativeLanguageSelect.value === targetLanguageSelect.value) {
                showFieldError(targetLanguageSelect, 
                    getOrCreateFeedback(targetLanguageSelect, 'language-feedback'), 
                    'La langue cible doit être différente de la langue native');
                return false;
            } else {
                showFieldSuccess(targetLanguageSelect, 
                    getOrCreateFeedback(targetLanguageSelect, 'language-feedback'), 
                    'Combinaison valide');
                return true;
            }
        }
        
        nativeLanguageSelect.addEventListener('change', validateLanguages);
        targetLanguageSelect.addEventListener('change', validateLanguages);
    }
    
    // Learning pace
    const paceSelect = document.querySelector('select[name="learning_pace"]');
    if (paceSelect) {
        paceSelect.addEventListener('change', () => {
            const pace = paceSelect.value;
            const paceText = {
                'slow': 'Rythme lent - Prenez votre temps',
                'normal': 'Rythme normal - Équilibré',
                'fast': 'Rythme rapide - Progression accélérée'
            };
            showTemporaryMessage(paceText[pace], 'info');
        });
    }
    
    // Focus areas
    const focusCheckboxes = [
        { name: 'focus_vocabulary', label: 'Vocabulaire' },
        { name: 'focus_grammar', label: 'Grammaire' },
        { name: 'focus_pronunciation', label: 'Prononciation' },
        { name: 'focus_listening', label: 'Compréhension orale' },
        { name: 'focus_conversation', label: 'Conversation' }
    ];
    
    focusCheckboxes.forEach(focus => {
        const checkbox = document.querySelector(`input[name="${focus.name}"]`);
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                // Count checked focuses
                const checkedCount = focusCheckboxes.filter(f => 
                    document.querySelector(`input[name="${f.name}"]`)?.checked
                ).length;
                
                if (checkedCount === 0) {
                    checkbox.checked = true;
                    showTemporaryMessage('Au moins un domaine doit être sélectionné', 'warning');
                } else {
                    const status = checkbox.checked ? 'activé' : 'désactivé';
                    showTemporaryMessage(`Focus ${focus.label} ${status}`, 'info');
                }
            });
        }
    });
    
    // Learning reminders
    const remindersToggle = document.querySelector('input[name="enable_learning_reminders"]');
    const reminderTimeField = document.querySelector('.reminder-time-field');
    
    if (remindersToggle && reminderTimeField) {
        function toggleReminderTime() {
            reminderTimeField.style.display = remindersToggle.checked ? 'block' : 'none';
        }
        
        remindersToggle.addEventListener('change', toggleReminderTime);
        toggleReminderTime(); // Initial state
    }
    
    console.log('[Learning Settings] Learning settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeLearningSettings();
});