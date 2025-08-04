/**
 * Notebook Settings JavaScript
 * Handles notebook-specific settings functionality
 */

function initializeNotebookSettings() {
    console.log('[Notebook Settings] Initializing notebook-specific settings...');
    
    // Auto-save interval
    const autoSaveIntervalSelect = document.querySelector('select[name="auto_save_interval"]');
    if (autoSaveIntervalSelect) {
        autoSaveIntervalSelect.addEventListener('change', () => {
            const interval = autoSaveIntervalSelect.value;
            const intervalText = {
                '30': '30 secondes',
                '60': '1 minute',
                '300': '5 minutes',
                'disabled': 'Désactivé'
            };
            showTemporaryMessage(`Sauvegarde automatique: ${intervalText[interval]}`, 'info');
        });
    }
    
    // Default notebook format
    const formatSelect = document.querySelector('select[name="default_notebook_format"]');
    if (formatSelect) {
        formatSelect.addEventListener('change', () => {
            const format = formatSelect.value;
            const formatIcons = {
                'rich_text': '📝',
                'markdown': '📄',
                'plain_text': '📋'
            };
            showTemporaryMessage(`Format par défaut: ${formatIcons[format]} ${format.replace('_', ' ')}`, 'info');
        });
    }
    
    // Sharing settings
    const publicShareToggle = document.querySelector('input[name="allow_public_sharing"]');
    const collaborativeEditToggle = document.querySelector('input[name="allow_collaborative_editing"]');
    
    if (publicShareToggle && collaborativeEditToggle) {
        // Disable collaborative editing if public sharing is off
        publicShareToggle.addEventListener('change', () => {
            if (!publicShareToggle.checked) {
                collaborativeEditToggle.checked = false;
                collaborativeEditToggle.disabled = true;
                showTemporaryMessage('Partage public désactivé', 'warning');
            } else {
                collaborativeEditToggle.disabled = false;
                showTemporaryMessage('Partage public activé', 'success');
            }
        });
        
        // Check initial state
        if (!publicShareToggle.checked) {
            collaborativeEditToggle.disabled = true;
        }
    }
    
    // Templates management
    const templatesToggle = document.querySelector('input[name="enable_templates"]');
    const templatesSection = document.querySelector('.templates-section');
    
    if (templatesToggle && templatesSection) {
        function toggleTemplatesSection() {
            templatesSection.style.display = templatesToggle.checked ? 'block' : 'none';
        }
        
        templatesToggle.addEventListener('change', toggleTemplatesSection);
        toggleTemplatesSection(); // Initial state
    }
    
    console.log('[Notebook Settings] Notebook settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeNotebookSettings();
});