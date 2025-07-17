/**
 * Voice Settings JavaScript
 * Handles voice-related settings and testing functions
 */

// Voice testing functions
function testVoice() {
    const utterance = new SpeechSynthesisUtterance('Test de l\'assistant vocal Linguify. Votre configuration fonctionne correctement !');
    
    const voiceSpeed = document.querySelector('select[name="speech_rate"]')?.value || 'normal';
    const voicePitch = document.querySelector('input[name="voice_pitch"]')?.value || 1;
    
    switch (voiceSpeed) {
        case 'slow':
            utterance.rate = 0.7;
            break;
        case 'fast':
            utterance.rate = 1.3;
            break;
        default:
            utterance.rate = 1.0;
    }
    
    utterance.pitch = voicePitch;
    utterance.lang = 'fr-FR';
    
    speechSynthesis.speak(utterance);
    showTemporaryMessage('Test vocal lancé', 'info');
}

function testMicrophone() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Votre navigateur ne supporte pas l\'accès au microphone.');
        return;
    }
    
    showTemporaryMessage('Test du microphone en cours...', 'info');
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            showTemporaryMessage('Microphone détecté et fonctionnel ! 🎤', 'success');
            stream.getTracks().forEach(track => track.stop());
        })
        .catch(error => {
            console.error('Erreur microphone:', error);
            showTemporaryMessage('Impossible d\'accéder au microphone. Vérifiez les permissions de votre navigateur.', 'error');
        });
}

// Voice settings specific initialization
function initializeVoiceSettings() {
    console.log('[Voice Settings] Initializing voice-specific settings...');
    
    // Setup voice test button
    const testVoiceBtn = document.querySelector('button[onclick*="testVoice"]');
    if (testVoiceBtn) {
        testVoiceBtn.removeAttribute('onclick');
        testVoiceBtn.addEventListener('click', testVoice);
    }
    
    // Setup microphone test button
    const testMicBtn = document.querySelector('button[onclick*="testMicrophone"]');
    if (testMicBtn) {
        testMicBtn.removeAttribute('onclick');
        testMicBtn.addEventListener('click', testMicrophone);
    }
    
    // Setup voice speed preview
    const voiceSpeedSelect = document.querySelector('select[name="speech_rate"]');
    if (voiceSpeedSelect) {
        voiceSpeedSelect.addEventListener('change', () => {
            const speedText = {
                'slow': 'Vitesse lente (0.7x)',
                'normal': 'Vitesse normale (1.0x)',
                'fast': 'Vitesse rapide (1.3x)'
            };
            showTemporaryMessage(speedText[voiceSpeedSelect.value] || 'Vitesse mise à jour', 'info');
        });
    }
    
    // Setup pitch preview
    const pitchInput = document.querySelector('input[name="voice_pitch"]');
    if (pitchInput) {
        let pitchTimeout;
        pitchInput.addEventListener('input', () => {
            clearTimeout(pitchTimeout);
            pitchTimeout = setTimeout(() => {
                const pitchValue = parseFloat(pitchInput.value);
                let pitchText = 'Tonalité normale';
                if (pitchValue < 0.8) pitchText = 'Voix grave';
                else if (pitchValue > 1.2) pitchText = 'Voix aiguë';
                showTemporaryMessage(`Tonalité: ${pitchText} (${pitchValue})`, 'info');
            }, 500);
        });
    }
    
    console.log('[Voice Settings] Voice settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeVoiceSettings();
});

// Make functions globally available
window.testVoice = testVoice;
window.testMicrophone = testMicrophone;