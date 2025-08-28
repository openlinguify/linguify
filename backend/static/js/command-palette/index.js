/**
 * Linguify Command Palette - Index
 * 
 * Importe tous les composants du command palette pour faciliter l'utilisation
 * Usage: <script src="{% static 'js/command-palette/index.js' %}"></script>
 */

// Auto-load all command palette components
(function() {
    const currentScript = document.currentScript || document.scripts[document.scripts.length - 1];
    const basePath = currentScript.src.replace('/index.js', '/');
    
    // Load command palette
    const commandPaletteScript = document.createElement('script');
    commandPaletteScript.src = basePath + 'linguify-command-palette.js';
    commandPaletteScript.async = false; // Ensure order
    document.head.appendChild(commandPaletteScript);
    
    // Load rich editor after command palette
    commandPaletteScript.onload = function() {
        const richEditorScript = document.createElement('script');
        richEditorScript.src = basePath + 'linguify-rich-editor.js';
        richEditorScript.async = false;
        document.head.appendChild(richEditorScript);
        
        // Dispatch ready event when both are loaded
        richEditorScript.onload = function() {
            const event = new CustomEvent('linguifyCommandPaletteReady', {
                detail: {
                    LinguifyCommandPalette: window.LinguifyCommandPalette,
                    LinguifyRichEditor: window.LinguifyRichEditor
                }
            });
            document.dispatchEvent(event);
        };
    };
})();

// Export convenience functions
window.LinguifyCommandPalette = window.LinguifyCommandPalette || null;
window.LinguifyRichEditor = window.LinguifyRichEditor || null;

// Helper function to initialize all components at once
window.initLinguifyEditors = function(options = {}) {
    document.addEventListener('linguifyCommandPaletteReady', function() {
        // Initialize all textareas with command palette
        document.querySelectorAll('textarea[data-command-palette]').forEach(textarea => {
            if (!textarea._linguifyCommandPalette) {
                textarea._linguifyCommandPalette = new window.LinguifyCommandPalette(textarea);
            }
        });
        
        // Initialize all rich editors
        document.querySelectorAll('[data-rich-editor]').forEach(container => {
            if (!container._linguifyRichEditor) {
                container._linguifyRichEditor = new window.LinguifyRichEditor(container, options);
            }
        });
    });
};