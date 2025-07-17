/**
 * Chat Settings JavaScript
 * Handles chat-specific settings functionality
 */

function initializeChatSettings() {
    console.log('[Chat Settings] Initializing chat-specific settings...');
    
    // Theme preview for chat
    const chatThemeSelect = document.querySelector('select[name="chat_theme"]');
    if (chatThemeSelect) {
        chatThemeSelect.addEventListener('change', () => {
            const theme = chatThemeSelect.value;
            // Preview chat theme
            const chatPreview = document.querySelector('.chat-preview');
            if (chatPreview) {
                chatPreview.className = `chat-preview chat-theme-${theme}`;
            }
            showTemporaryMessage(`Thème chat: ${theme}`, 'info');
        });
    }
    
    // Message retention settings
    const retentionSelect = document.querySelector('select[name="message_retention"]');
    if (retentionSelect) {
        retentionSelect.addEventListener('change', () => {
            const retention = retentionSelect.value;
            const retentionText = {
                '7_days': '7 jours',
                '30_days': '30 jours',
                '90_days': '90 jours',
                'forever': 'Indéfiniment'
            };
            showTemporaryMessage(`Conservation des messages: ${retentionText[retention]}`, 'info');
        });
    }
    
    // Auto-translate toggle
    const autoTranslateToggle = document.querySelector('input[name="auto_translate"]');
    if (autoTranslateToggle) {
        autoTranslateToggle.addEventListener('change', () => {
            const status = autoTranslateToggle.checked ? 'activée' : 'désactivée';
            showTemporaryMessage(`Traduction automatique ${status}`, 'info');
        });
    }
    
    console.log('[Chat Settings] Chat settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeChatSettings();
});