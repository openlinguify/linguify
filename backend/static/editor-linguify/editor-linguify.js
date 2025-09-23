/**
 * Linguify Editor - Editor.js implementation for Linguify Platform
 *
 * This file configures Editor.js with custom tools and settings
 * for use across all Linguify modules
 *
 * @version 2.0.0
 * @author Linguify Team
 */

class LinguifyEditor {
    constructor(holderId, config = {}) {
        this.holderId = holderId;
        this.editor = null;
        this.config = config;
        this.isReady = false;

        // Default configuration
        this.defaultConfig = {
            /**
             * Id of Element that should contain Editor instance
             */
            holder: holderId,

            /**
             * Placeholder text
             */
            placeholder: 'Tapez "/" pour voir les commandes disponibles...',

            /**
             * Enable autofocus
             */
            autofocus: true,

            /**
             * Initial editor data
             */
            data: config.data || {},

            /**
             * onReady callback
             */
            onReady: () => {
                this.isReady = true;
                console.log('LinguifyEditor is ready!');
                if (config.onReady) config.onReady();
            },

            /**
             * onChange callback
             */
            onChange: async (api, event) => {
                if (config.onChange) {
                    const data = await this.save();
                    config.onChange(data, api, event);
                }
            },

            /**
             * Tools configuration
             */
            tools: {
                /**
                 * Header Tool
                 */
                header: {
                    class: Header,
                    inlineToolbar: true,
                    config: {
                        placeholder: 'Entrez un titre...',
                        levels: [1, 2, 3, 4, 5, 6],
                        defaultLevel: 2
                    },
                    shortcut: 'CMD+SHIFT+H'
                },

                /**
                 * List Tool
                 */
                list: {
                    class: List,
                    inlineToolbar: true,
                    config: {
                        defaultStyle: 'unordered'
                    },
                    shortcut: 'CMD+SHIFT+L'
                },

                /**
                 * Checklist Tool
                 */
                checklist: {
                    class: Checklist,
                    inlineToolbar: true,
                    shortcut: 'CMD+SHIFT+C'
                },

                /**
                 * Quote Tool
                 */
                quote: {
                    class: Quote,
                    inlineToolbar: true,
                    config: {
                        quotePlaceholder: 'Entrez une citation...',
                        captionPlaceholder: 'Auteur de la citation'
                    },
                    shortcut: 'CMD+SHIFT+Q'
                },

                /**
                 * Code Tool
                 */
                code: {
                    class: CodeTool,
                    config: {
                        placeholder: 'Entrez votre code...'
                    },
                    shortcut: 'CMD+SHIFT+K'
                },

                /**
                 * Delimiter Tool
                 */
                delimiter: {
                    class: Delimiter,
                    shortcut: 'CMD+SHIFT+D'
                },

                /**
                 * Table Tool
                 */
                table: {
                    class: Table,
                    inlineToolbar: true,
                    config: {
                        rows: 2,
                        cols: 3,
                        withHeadings: true
                    },
                    shortcut: 'CMD+SHIFT+T'
                },

                /**
                 * Warning Tool
                 */
                warning: {
                    class: Warning,
                    inlineToolbar: true,
                    config: {
                        titlePlaceholder: 'Titre',
                        messagePlaceholder: 'Message',
                    }
                },

                /**
                 * Marker Tool (Highlighter)
                 */
                marker: {
                    class: Marker,
                    shortcut: 'CMD+SHIFT+M'
                },

                /**
                 * Inline Code Tool
                 */
                inlineCode: {
                    class: InlineCode,
                    shortcut: 'CMD+SHIFT+I'
                }
            },

            /**
             * Inline Toolbar configuration
             */
            inlineToolbar: ['bold', 'italic', 'underline', 'link', 'marker', 'inlineCode'],

            /**
             * Editor.js i18n configuration for French
             */
            i18n: {
                /**
                 * Text direction
                 */
                direction: "ltr",

                /**
                 * Translations
                 */
                messages: {
                    /**
                     * UI elements translation
                     */
                    ui: {
                        "blockTunes": {
                            "toggler": {
                                "Click to tune": "Cliquer pour ajuster",
                                "or drag to move": "ou glisser pour déplacer"
                            },
                        },
                        "inlineToolbar": {
                            "converter": {
                                "Convert to": "Convertir en"
                            }
                        },
                        "toolbar": {
                            "toolbox": {
                                "Add": "Ajouter",
                                "Filter": "Filtrer",
                                "Nothing found": "Aucun résultat"
                            }
                        },
                        "popover": {
                            "Filter": "Filtrer",
                            "Nothing found": "Aucun résultat"
                        }
                    },

                    /**
                     * Tools names for Toolbox
                     */
                    toolNames: {
                        "Text": "Texte",
                        "Heading": "Titre",
                        "List": "Liste",
                        "Warning": "Avertissement",
                        "Checklist": "Liste de tâches",
                        "Quote": "Citation",
                        "Code": "Code",
                        "Delimiter": "Séparateur",
                        "Table": "Tableau",
                        "Link": "Lien",
                        "Marker": "Surligneur",
                        "Bold": "Gras",
                        "Italic": "Italique",
                        "InlineCode": "Code inline"
                    },

                    /**
                     * Tools shortcuts
                     */
                    tools: {
                        "warning": {
                            "Title": "Titre",
                            "Message": "Message"
                        },
                        "link": {
                            "Add a link": "Ajouter un lien"
                        },
                        "stub": {
                            "The block can not be displayed correctly.": "Ce bloc ne peut pas être affiché correctement."
                        },
                        "code": {
                            "Enter a code": "Entrez du code"
                        },
                        "quote": {
                            "Enter a quote": "Entrez une citation",
                            "Enter a caption": "Entrez une légende"
                        },
                        "list": {
                            "Ordered": "Ordonnée",
                            "Unordered": "Non ordonnée"
                        },
                        "header": {
                            "Header": "Titre",
                            "Enter a header": "Entrez un titre"
                        },
                        "checklist": {
                            "Enter a to-do": "Entrez une tâche"
                        },
                        "table": {
                            "Add row above": "Ajouter ligne au-dessus",
                            "Add row below": "Ajouter ligne en-dessous",
                            "Delete row": "Supprimer la ligne",
                            "Add column to the left": "Ajouter colonne à gauche",
                            "Add column to the right": "Ajouter colonne à droite",
                            "Delete column": "Supprimer la colonne",
                            "With headings": "Avec en-têtes",
                            "Without headings": "Sans en-têtes"
                        }
                    }
                }
            }
        };

        // Merge configurations
        this.editorConfig = { ...this.defaultConfig, ...config };
    }

    /**
     * Initialize the editor
     */
    async init() {
        try {
            // Wait for Editor.js to be loaded
            await this.waitForEditorJS();

            // Create editor instance
            this.editor = new EditorJS(this.editorConfig);

            // Wait for editor to be ready
            await this.editor.isReady;

            console.log('✅ LinguifyEditor initialized successfully');
            return this.editor;

        } catch (error) {
            console.error('❌ Failed to initialize LinguifyEditor:', error);
            throw error;
        }
    }

    /**
     * Wait for Editor.js and all tools to be loaded
     */
    async waitForEditorJS() {
        const maxWait = 10000; // 10 seconds
        const interval = 100; // Check every 100ms
        let elapsed = 0;

        while (elapsed < maxWait) {
            if (typeof EditorJS !== 'undefined' &&
                typeof Header !== 'undefined' &&
                typeof List !== 'undefined' &&
                typeof Checklist !== 'undefined' &&
                typeof Quote !== 'undefined' &&
                typeof CodeTool !== 'undefined' &&
                typeof Delimiter !== 'undefined' &&
                typeof Table !== 'undefined' &&
                typeof Warning !== 'undefined' &&
                typeof Marker !== 'undefined' &&
                typeof InlineCode !== 'undefined') {
                return;
            }
            await new Promise(resolve => setTimeout(resolve, interval));
            elapsed += interval;
        }

        throw new Error('Editor.js dependencies failed to load');
    }

    /**
     * Save editor data
     */
    async save() {
        if (!this.editor || !this.isReady) {
            console.warn('Editor not ready');
            return null;
        }

        try {
            const outputData = await this.editor.save();
            console.log('Editor data saved:', outputData);
            return outputData;
        } catch (error) {
            console.error('Saving failed:', error);
            return null;
        }
    }

    /**
     * Clear editor content
     */
    async clear() {
        if (!this.editor || !this.isReady) {
            console.warn('Editor not ready');
            return;
        }

        await this.editor.clear();
    }

    /**
     * Render data to editor
     */
    async render(data) {
        if (!this.editor || !this.isReady) {
            console.warn('Editor not ready');
            return;
        }

        await this.editor.render(data);
    }

    /**
     * Destroy editor instance
     */
    destroy() {
        if (this.editor) {
            this.editor.destroy();
            this.editor = null;
            this.isReady = false;
        }
    }

    /**
     * Focus the editor
     */
    focus() {
        if (this.editor && this.isReady) {
            // Focus on the last block
            const blocksCount = this.editor.blocks.getBlocksCount();
            if (blocksCount > 0) {
                this.editor.caret.setToBlock(blocksCount - 1, 'end');
            }
        }
    }

    /**
     * Get current block
     */
    getCurrentBlock() {
        if (this.editor && this.isReady) {
            return this.editor.blocks.getCurrentBlockIndex();
        }
        return -1;
    }
}

// Export for use in Alpine.js components
window.LinguifyEditor = LinguifyEditor;