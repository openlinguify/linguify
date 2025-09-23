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
            placeholder: 'Commencez à écrire ou tapez "/" pour les commandes...',

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
             * Log level
             */
            logLevel: 'ERROR',

            /**
             * Tools configuration
             */
            tools: {
                /**
                 * Paragraph Tool (with improvements)
                 */
                paragraph: {
                    class: Paragraph,
                    inlineToolbar: true,
                    config: {
                        placeholder: 'Tapez "/" pour les commandes ou commencez à écrire...'
                    }
                },

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
                    shortcut: 'CMD+SHIFT+H',
                    toolbox: {
                        title: '📝 Titre',
                        icon: '<svg width="17" height="15" viewBox="0 0 17 15"><path d="M9.4 0L7.6 0 7.6 15 9.4 15 9.4 7.5 15.5 7.5 15.5 15 17 15 17 0 15.5 0 15.5 6 9.4 6 9.4 0ZM0 2L0 3.5 4.5 3.5 4.5 15 6 15 6 3.5 10.5 3.5 10.5 2 0 2Z"/></svg>'
                    }
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
                },


                /**
                 * Embed Tool (YouTube, Vimeo, etc.)
                 */
                embed: {
                    class: Embed,
                    inlineToolbar: true,
                    config: {
                        services: {
                            youtube: true,
                            vimeo: true,
                            codepen: true,
                            twitter: true,
                            instagram: true,
                            gfycat: true,
                            imgur: true,
                            pinterest: true
                        }
                    },
                    toolbox: {
                        title: '🎥 Vidéo/Embed',
                        icon: '<svg width="17" height="15" viewBox="0 0 17 15"><path d="M10.918 13.933a.6.6 0 0 1-.858.185l-4.238-2.763a.6.6 0 0 1 0-.932l4.238-2.763a.6.6 0 0 1 .911.466v5.621a.6.6 0 0 1-.053.186z"/><rect x="1.4" y="2.4" width="12.2" height="10.2" rx="1.5" stroke="currentColor" stroke-width="1.2" fill="none"/></svg>'
                    }
                },

                /**
                 * Simple Image Tool
                 */
                image: {
                    class: SimpleImage,
                    inlineToolbar: true,
                    config: {
                        placeholder: 'Collez l\'URL de l\'image',
                        buttonContent: 'Sélectionner une image',
                        uploader: false
                    },
                    toolbox: {
                        title: '🖼️ Image',
                        icon: '<svg width="17" height="15" viewBox="0 0 17 15"><rect x="1" y="3" width="14" height="9" stroke="currentColor" stroke-width="1" fill="none"/><circle cx="5.5" cy="6.5" r="1.5" fill="currentColor"/><polyline points="11 9, 8 6, 4 10" stroke="currentColor" stroke-width="1" fill="none"/></svg>'
                    }
                },

                /**
                 * Raw HTML Tool
                 */
                raw: {
                    class: RawTool,
                    toolbox: {
                        title: '📄 HTML',
                        icon: '<svg width="17" height="15" viewBox="0 0 17 15"><path d="M13.133 14h-9.267c-1.495 0-2.585-.983-2.585-2.333v-8.334c0-1.35 1.09-2.333 2.585-2.333h9.267c1.495 0 2.585.983 2.585 2.333v8.334c0 1.35-1.09 2.333-2.585 2.333z"/><path d="M4.65 7.333L6.167 10l1.517-2.667" stroke="#fff" stroke-linecap="round"/><path d="M11.3 5L9.783 7.667 11.3 10.333" stroke="#fff" stroke-linecap="round"/></svg>'
                    }
                }
            },

            /**
             * Inline Toolbar configuration
             */
            inlineToolbar: ['bold', 'italic', 'link', 'marker', 'inlineCode'],

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
                typeof Paragraph !== 'undefined' &&
                typeof List !== 'undefined' &&
                typeof Checklist !== 'undefined' &&
                typeof Quote !== 'undefined' &&
                typeof CodeTool !== 'undefined' &&
                typeof Delimiter !== 'undefined' &&
                typeof Table !== 'undefined' &&
                typeof Warning !== 'undefined' &&
                typeof Marker !== 'undefined' &&
                typeof InlineCode !== 'undefined' &&
                typeof Embed !== 'undefined' &&
                typeof SimpleImage !== 'undefined' &&
                typeof RawTool !== 'undefined') {
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