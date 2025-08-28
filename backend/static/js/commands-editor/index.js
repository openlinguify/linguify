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
        // Delay initialization to ensure proper script loading order
        setTimeout(initializeCommandsEditor, 100);
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
        return new Promise((resolve, reject) => {
            if (window.LinguifyEditor) {
                // Already loaded, initialize immediately
                const editor = new LinguifyEditor(holderId, options);
                editor.init().then(() => resolve(editor)).catch(reject);
            } else {
                // Wait for the ready event
                document.addEventListener('linguifyCommandsEditorReady', async () => {
                    try {
                        const editor = new LinguifyEditor(holderId, options);
                        await editor.init();
                        resolve(editor);
                    } catch (error) {
                        reject(error);
                    }
                });
            }
        });
    };
    
    window.initLinguifyEditorWithContent = function(holderId, content, options = {}) {
        return new Promise((resolve, reject) => {
            if (window.LinguifyEditor) {
                // Already loaded, initialize immediately
                LinguifyEditor.createFromContent(holderId, content, options)
                    .then(resolve).catch(reject);
            } else {
                // Wait for the ready event
                document.addEventListener('linguifyCommandsEditorReady', async () => {
                    try {
                        const editor = await LinguifyEditor.createFromContent(holderId, content, options);
                        resolve(editor);
                    } catch (error) {
                        reject(error);
                    }
                });
            }
        });
    };
    
})();