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
        this.init();
    }
    
    init() {
        // Wait for all Editor.js tools to be loaded
        if (typeof EditorJS === 'undefined') {
            console.error('EditorJS not loaded');
            return;
        }
        
        this.editor = new EditorJS({
            holderId: this.holderId,
            placeholder: this.options.placeholder,
            autofocus: this.options.autofocus,
            tools: this.getToolsConfig(),
            inlineToolbar: ['marker', 'inlineCode'],
            data: { blocks: [] }
        });
    }
    
    getToolsConfig() {
        return {
            // ===== Format =====
            header: {
                class: Header,
                inlineToolbar: true,
                config: {
                    placeholder: 'Titre...',
                    levels: [1, 2, 3, 4, 5, 6],
                    defaultLevel: 2
                },
                shortcut: 'CMD+SHIFT+H'
            },
            paragraph: {
                class: Paragraph,
                inlineToolbar: true
            },
            
            // ===== Structure =====
            list: {
                class: List,
                inlineToolbar: true,
                config: {
                    defaultStyle: 'unordered'
                }
            },
            checklist: {
                class: Checklist,
                inlineToolbar: true
            },
            quote: {
                class: Quote,
                inlineToolbar: true,
                shortcut: 'CMD+SHIFT+O',
                config: {
                    quotePlaceholder: 'Citation...',
                    captionPlaceholder: 'Auteur...'
                }
            },
            delimiter: {
                class: Delimiter
            },
            table: {
                class: Table,
                inlineToolbar: true,
                config: {
                    rows: 2,
                    cols: 3
                }
            },
            code: {
                class: CodeTool,
                config: {
                    placeholder: 'Entrez votre code...'
                }
            },
            
            // ===== Navigation/Média =====
            linkTool: {
                class: LinkTool,
                config: {
                    endpoint: '/api/link-preview' // Endpoint to be implemented
                }
            },
            image: {
                class: ImageTool,
                config: {
                    endpoints: {
                        byFile: '/api/upload-image', // Endpoint to be implemented
                        byUrl: '/api/image-by-url'   // Endpoint to be implemented
                    }
                }
            },
            
            // ===== Bannières/Alertes =====
            alert: {
                class: Alert,
                inlineToolbar: true,
                shortcut: 'CMD+SHIFT+A',
                config: {
                    alertTypes: ['primary', 'secondary', 'info', 'success', 'warning', 'danger'],
                    defaultType: 'info',
                    messagePlaceholder: 'Tapez votre message...'
                }
            },
            
            // ===== Inline Tools =====
            marker: {
                class: Marker
            },
            inlineCode: {
                class: InlineCode
            }
        };
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
        const editor = new LinguifyEditor(holderId, options);
        
        // Wait for editor to be ready
        if (editor.editor) {
            await editor.editor.isReady;
            
            if (content) {
                try {
                    // Try to parse as JSON first
                    const parsedData = JSON.parse(content);
                    await editor.render(parsedData);
                } catch (e) {
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
        }
        
        return editor;
    }
}

// Export for global use
window.LinguifyEditor = LinguifyEditor;