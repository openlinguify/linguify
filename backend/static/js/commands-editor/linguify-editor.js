/**
 * Linguify Editor.js Configuration
 * Centralized Editor.js setup with all tools and styling
 */

class LinguifyEditor {
    constructor(holderId, options = {}) {
        this.holderId = holderId;
        this.options = {
            placeholder: 'Commencez à taper votre description...',
            autofocus: true,
            ...options
        };
        
        this.editor = null;
        // Don't auto-init in constructor - wait for async initialization
    }
    
    async init() {
        // Wait for all Editor.js tools to be loaded
        if (typeof EditorJS === 'undefined') {
            console.error('❌ EditorJS not loaded');
            throw new Error('EditorJS not available');
        }
        
        // Check if target element exists
        const targetElement = document.getElementById(this.holderId);
        if (!targetElement) {
            console.error('❌ Target element not found:', this.holderId);
            throw new Error(`Target element '${this.holderId}' not found`);
        }
        
        console.log('🔧 Initializing LinguifyEditor with:', {
            holderId: this.holderId,
            targetElement: targetElement,
            options: this.options
        });
        
        try {
            const tools = this.getToolsConfig();
            console.log('🛠️ Available tools:', Object.keys(tools));
            
            // Check which inline tools are actually available
            const availableInlineTools = [];
            if (tools.marker) availableInlineTools.push('marker');
            if (tools.inlineCode) availableInlineTools.push('inlineCode');
            
            console.log('🔧 Inline toolbar will use:', availableInlineTools);
            
            this.editor = new EditorJS({
                holder: this.holderId,
                placeholder: this.options.placeholder,
                autofocus: this.options.autofocus,
                tools: tools,
                inlineToolbar: availableInlineTools.length > 0 ? availableInlineTools : true,
                data: { blocks: [] },
                onChange: (api, event) => {
                    console.log('📝 Editor content changed');
                },
                // Configuration pour améliorer l'affichage des toolbars
                defaultBlock: 'paragraph',
                minHeight: 0,
                logLevel: 'VERBOSE',
                // Réactiver complètement la toolbar pour les commandes slash
                // mais on cachera visuellement les boutons avec CSS
            });
            
            // Wait for the editor to be ready
            await this.editor.isReady;
            console.log('✅ EditorJS ready for:', this.holderId);
            
            // Add debug event listeners
            const editorElement = document.getElementById(this.holderId);
            if (editorElement) {
                // Debug sélection de texte
                editorElement.addEventListener('mouseup', () => {
                    setTimeout(() => {
                        const selection = window.getSelection();
                        if (selection.toString().length > 0) {
                            console.log('📝 Text selected:', selection.toString());
                            console.log('🔍 Looking for inline toolbar...');
                            const inlineToolbar = document.querySelector('.ce-inline-toolbar');
                            console.log('🔧 Inline toolbar found:', !!inlineToolbar);
                            if (inlineToolbar) {
                                console.log('👁️ Inline toolbar visible:', 
                                    window.getComputedStyle(inlineToolbar).display !== 'none');
                            }
                        }
                    }, 100);
                });
                
                // Debug commandes slash
                editorElement.addEventListener('keydown', (e) => {
                    if (e.key === '/') {
                        console.log('🔀 Slash key pressed!');
                        setTimeout(() => {
                            const popover = document.querySelector('.ce-popover');
                            const toolbox = document.querySelector('.ce-toolbox');
                            console.log('📋 Popover found:', !!popover);
                            console.log('🧰 Toolbox found:', !!toolbox);
                        }, 100);
                    }
                });
            }
            
        } catch (error) {
            console.error('❌ EditorJS initialization failed:', error);
            throw error;
        }
    }
    
    getToolsConfig() {
        const tools = {};
        
        // Check which tools are available and add them safely
        if (typeof window.Header !== 'undefined') {
            tools.header = {
                class: window.Header,
                inlineToolbar: true,
                config: {
                    placeholder: 'Titre...',
                    levels: [1, 2, 3, 4, 5, 6],
                    defaultLevel: 2
                },
                shortcut: 'CMD+SHIFT+H'
            };
        }
        
        if (typeof window.Paragraph !== 'undefined') {
            tools.paragraph = {
                class: window.Paragraph,
                inlineToolbar: true
            };
        }
        
        if (typeof window.List !== 'undefined') {
            tools.list = {
                class: window.List,
                inlineToolbar: true,
                config: {
                    defaultStyle: 'unordered'
                }
            };
        }
        
        if (typeof window.Checklist !== 'undefined') {
            tools.checklist = {
                class: window.Checklist,
                inlineToolbar: true
            };
        }
        
        if (typeof window.Quote !== 'undefined') {
            tools.quote = {
                class: window.Quote,
                inlineToolbar: true,
                shortcut: 'CMD+SHIFT+O',
                config: {
                    quotePlaceholder: 'Citation...',
                    captionPlaceholder: 'Auteur...'
                }
            };
        }
        
        if (typeof window.Delimiter !== 'undefined') {
            tools.delimiter = {
                class: window.Delimiter
            };
        }
        
        if (typeof window.Table !== 'undefined') {
            tools.table = {
                class: window.Table,
                inlineToolbar: true,
                config: {
                    rows: 2,
                    cols: 3
                }
            };
        }
        
        if (typeof window.CodeTool !== 'undefined') {
            tools.code = {
                class: window.CodeTool,
                config: {
                    placeholder: 'Entrez votre code...'
                }
            };
        }
        
        // Inline tools - Debug what's available
        console.log('🔍 Checking inline tools availability:');
        console.log('  - Marker:', typeof window.Marker !== 'undefined');
        console.log('  - InlineCode:', typeof window.InlineCode !== 'undefined');
        
        if (typeof window.Marker !== 'undefined') {
            tools.marker = {
                class: window.Marker,
                shortcut: 'CMD+SHIFT+M'
            };
            console.log('✅ Marker tool configured');
        } else {
            console.warn('❌ Marker tool not available');
        }
        
        if (typeof window.InlineCode !== 'undefined') {
            tools.inlineCode = {
                class: window.InlineCode,
                shortcut: 'CMD+SHIFT+C'
            };
            console.log('✅ InlineCode tool configured');
        } else {
            console.warn('❌ InlineCode tool not available');
        }
        
        console.log('🛠️ Tools configured:', Object.keys(tools));
        return tools;
    }
    
    // Public methods
    async save() {
        if (!this.editor) return null;
        try {
            return await this.editor.save();
        } catch (error) {
            console.error('Saving failed: ', error);
            return null;
        }
    }
    
    async render(data) {
        if (!this.editor) return;
        try {
            await this.editor.render(data);
        } catch (error) {
            console.error('Rendering failed: ', error);
        }
    }
    
    async clear() {
        if (!this.editor) return;
        try {
            await this.editor.clear();
        } catch (error) {
            console.error('Clearing failed: ', error);
        }
    }
    
    destroy() {
        if (this.editor && this.editor.destroy) {
            this.editor.destroy();
        }
    }
    
    // Static method to initialize from existing content
    static async createFromContent(holderId, content, options = {}) {
        console.log('📝 Creating LinguifyEditor with content:', {
            holderId,
            contentLength: content ? content.length : 0,
            options
        });
        
        const editor = new LinguifyEditor(holderId, options);
        
        // Initialize the editor first
        await editor.init();
        
        if (content && content.trim()) {
            try {
                console.log('🔍 Attempting to parse content as JSON...');
                // Try to parse as JSON first
                const parsedData = JSON.parse(content);
                console.log('✅ Content parsed as JSON, rendering...');
                await editor.render(parsedData);
            } catch (e) {
                console.log('📝 Content is not JSON, creating paragraph block...');
                // If not JSON, create a simple paragraph block
                await editor.render({
                    blocks: [
                        {
                            type: 'paragraph',
                            data: {
                                text: content
                            }
                        }
                    ]
                });
            }
        }
        
        return editor;
    }
}

// Export for global use
window.LinguifyEditor = LinguifyEditor;