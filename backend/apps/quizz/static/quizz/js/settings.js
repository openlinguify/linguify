/**
 * Quiz Settings JavaScript
 * Handles quiz-specific settings functionality
 */

function initializeQuizSettings() {
    console.log('[Quiz Settings] Initializing quiz-specific settings...');
    
    // Timer settings
    const timedQuizToggle = document.querySelector('input[name="timed_quiz"]');
    const quizDurationField = document.querySelector('.quiz-duration-field');
    
    if (timedQuizToggle && quizDurationField) {
        // Show/hide duration field based on timed quiz setting
        function toggleDurationField() {
            if (timedQuizToggle.checked) {
                quizDurationField.style.display = 'block';
                showTemporaryMessage('Mode chronométré activé', 'info');
            } else {
                quizDurationField.style.display = 'none';
                showTemporaryMessage('Mode chronométré désactivé', 'info');
            }
        }
        
        timedQuizToggle.addEventListener('change', toggleDurationField);
        // Initial state
        toggleDurationField();
    }
    
    // Difficulty settings
    const difficultySelect = document.querySelector('select[name="quiz_difficulty"]');
    if (difficultySelect) {
        difficultySelect.addEventListener('change', () => {
            const difficulty = difficultySelect.value;
            const difficultyText = {
                'easy': 'Facile',
                'medium': 'Moyen',
                'hard': 'Difficile',
                'mixed': 'Mixte'
            };
            showTemporaryMessage(`Difficulté: ${difficultyText[difficulty]}`, 'info');
        });
    }
    
    // Questions per quiz
    const questionsInput = document.querySelector('input[name="questions_per_quiz"]');
    if (questionsInput) {
        questionsInput.addEventListener('change', () => {
            const value = parseInt(questionsInput.value);
            if (value < 5) {
                showFieldError(questionsInput, getOrCreateFeedback(questionsInput, 'questions-feedback'), 'Minimum 5 questions');
                questionsInput.value = 5;
            } else if (value > 50) {
                showFieldError(questionsInput, getOrCreateFeedback(questionsInput, 'questions-feedback'), 'Maximum 50 questions');
                questionsInput.value = 50;
            } else {
                showFieldSuccess(questionsInput, getOrCreateFeedback(questionsInput, 'questions-feedback'), `${value} questions par quiz`);
            }
        });
    }
    
    // Audio feedback toggle
    const audioFeedbackToggle = document.querySelector('input[name="audio_feedback"]');
    if (audioFeedbackToggle) {
        audioFeedbackToggle.addEventListener('change', () => {
            const status = audioFeedbackToggle.checked ? 'activé' : 'désactivé';
            showTemporaryMessage(`Feedback audio ${status}`, 'info');
            
            // Play a sample sound if enabled
            if (audioFeedbackToggle.checked) {
                const audio = new Audio('/static/sounds/correct.mp3');
                audio.volume = 0.3;
                audio.play().catch(e => console.log('Audio preview failed:', e));
            }
        });
    }
    
    console.log('[Quiz Settings] Quiz settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeQuizSettings();
});