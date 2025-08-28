/**
 * Linguify Commands Editor - Main Entry Point
 * Auto-loads all dependencies and provides easy initialization
 */

(function() {
    'use strict';
    
    // Configuration
    const COMMANDS_EDITOR_PATH = '/static/js/commands-editor/';
    
    // Auto-detect base path from current script
    const getCurrentScript = () => {
        return document.currentScript || document.scripts[document.scripts.length - 1];
    };
    
    const getBasePath = () => {
        const script = getCurrentScript();
        if (script && script.src) {
            return script.src.replace('/index.js', '/');
        }
        return COMMANDS_EDITOR_PATH;
    };
    
    // Load dependencies
    const loadDependencies = async () => {
        const basePath = getBasePath();
        
        // Load CDN loader first
        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = basePath + 'editor-cdn.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
        
        // Load all Editor.js dependencies
        await EditorJSLoader.init();
        
        // Load Linguify Editor wrapper
        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = basePath + 'linguify-editor.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCommandsEditor);
    } else {
        initializeCommandsEditor();
    }
    
    async function initializeCommandsEditor() {
        try {
            await loadDependencies();
            
            // Dispatch ready event
            const event = new CustomEvent('linguifyCommandsEditorReady', {
                detail: {
                    LinguifyEditor: window.LinguifyEditor,
                    EditorJSLoader: window.EditorJSLoader
                }
            });
            document.dispatchEvent(event);
            
            console.log('✅ Linguify Commands Editor ready!');
            
        } catch (error) {
            console.error('❌ Failed to initialize Commands Editor:', error);
        }
    }
    
    // Helper functions for easy initialization
    window.initLinguifyEditor = function(holderId, options = {}) {
        return new Promise((resolve) => {
            document.addEventListener('linguifyCommandsEditorReady', () => {
                const editor = new LinguifyEditor(holderId, options);
                resolve(editor);
            });
        });
    };
    
    window.initLinguifyEditorWithContent = function(holderId, content, options = {}) {
        return new Promise((resolve) => {
            document.addEventListener('linguifyCommandsEditorReady', async () => {
                const editor = await LinguifyEditor.createFromContent(holderId, content, options);
                resolve(editor);
            });
        });
    };
    
})();