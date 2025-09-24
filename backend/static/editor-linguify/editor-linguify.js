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
        this.saveTimeout = null;

        // Default configuration
        this.defaultConfig = {
            /**
             * Id of Element that should contain Editor instance
             */
            holder: holderId,

            /**
             * Placeholder text
             */
            placeholder: 'Tapez "/" pour les commandes ou commencez à écrire...',

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
            onChange: (api, event) => {
                if (config.onChange) {
                    // Use a debounced approach to avoid calling save() too frequently
                    if (this.saveTimeout) {
                        clearTimeout(this.saveTimeout);
                    }
                    this.saveTimeout = setTimeout(async () => {
                        try {
                            // Call save on the API to get the actual content
                            const data = await api.saver.save();
                            config.onChange(data, api, event);
                        } catch (error) {
                            console.error('Error in onChange callback:', error);
                            // Try alternative approach: pass the API so the callback can handle it
                            config.onChange(null, api, event);
                        }
                    }, 100); // Small delay to avoid too many calls
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
                        title: 'Titre',
                        icon: '<svg width="17" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M5 4v3h5.5v12h3V7H19V4z"/></svg>'
                    }
                },

                /**
                 * List Tool (with nesting support)
                 */
                list: {
                    class: NestedList,
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
                        title: 'Image',
                        icon: '<svg width="17" height="15" viewBox="0 0 17 15"><rect x="1" y="3" width="14" height="9" stroke="currentColor" stroke-width="1" fill="none"/><circle cx="5.5" cy="6.5" r="1.5" fill="currentColor"/><polyline points="11 9, 8 6, 4 10" stroke="currentColor" stroke-width="1" fill="none"/></svg>'
                    }
                },

                /**
                 * Raw HTML Tool
                 */
                raw: {
                    class: RawTool,
                    toolbox: {
                        title: 'HTML',
                        icon: '<svg width="17" height="15" viewBox="0 0 17 15"><path d="M13.133 14h-9.267c-1.495 0-2.585-.983-2.585-2.333v-8.334c0-1.35 1.09-2.333 2.585-2.333h9.267c1.495 0 2.585.983 2.585 2.333v8.334c0 1.35-1.09 2.333-2.585 2.333z"/><path d="M4.65 7.333L6.167 10l1.517-2.667" stroke="#fff" stroke-linecap="round"/><path d="M11.3 5L9.783 7.667 11.3 10.333" stroke="#fff" stroke-linecap="round"/></svg>'
                    }
                },

                /**
                 * Link Tool
                 */
                linkTool: {
                    class: LinkTool,
                    config: {
                        endpoint: '/notebook/api/fetch-url-meta/' // For URL preview
                    }
                },

            },

            /**
             * Inline Toolbar configuration - Enhanced with more tools
             */
            inlineToolbar: ['bold', 'italic', 'link', 'marker', 'inlineCode'],

            /**
             * Block tunes configuration
             */
            tunes: [],

            /**
             * Hide toolbar completely - using slash commands instead
             */
            toolbar: false,

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
                                "Click to tune": "",
                                "or drag to move": ""
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

            // Setup slash command functionality
            this.setupSlashCommands();

            // Masquer définitivement le bouton plus avec CSS agressif
            this.hideToolbarElements();

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
                typeof NestedList !== 'undefined' &&
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
                typeof RawTool !== 'undefined' &&
                typeof LinkTool !== 'undefined') {
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

            // Validation des données pour les nouveaux outils
            if (outputData && outputData.blocks) {
                outputData.blocks.forEach((block, index) => {
                    try {
                        // Vérifier que chaque bloc peut être sérialisé en JSON
                        JSON.stringify(block);
                    } catch (blockError) {
                        console.error(`Block ${index} serialization error:`, blockError, block);
                        // Nettoyer le bloc problématique
                        if (block.data && typeof block.data === 'object') {
                            // Garder seulement les propriétés sérialisables
                            block.data = JSON.parse(JSON.stringify(block.data));
                        }
                    }
                });
            }

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

        // Clean up slash menu
        this.closeSlashMenu();

        // Clean up toolbar observer
        if (this.toolbarObserver) {
            this.toolbarObserver.disconnect();
            this.toolbarObserver = null;
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

    /**
     * Remove all toolbar elements completely
     */
    hideToolbarElements() {
        // Fonction pour supprimer les éléments toolbar
        const removeToolbarElements = () => {
            const selectorsToRemove = [
                '.ce-toolbar',
                '.ce-toolbar__plus',
                '.ce-toolbar__settings-btn',
                '.ce-toolbar__content',
                '.ce-toolbar__actions'
            ];

            selectorsToRemove.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.remove());
            });
        };

        // Supprimer immédiatement
        removeToolbarElements();

        // Observer pour supprimer les éléments qui apparaissent dynamiquement
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Supprimer les toolbars qui apparaissent dynamiquement
                        if (node.classList && (
                            node.classList.contains('ce-toolbar') ||
                            node.classList.contains('ce-toolbar__plus') ||
                            node.classList.contains('ce-toolbar__settings-btn') ||
                            node.classList.contains('ce-toolbar__content') ||
                            node.classList.contains('ce-toolbar__actions')
                        )) {
                            node.remove();
                        }

                        // Chercher et supprimer dans les enfants aussi
                        const toolbarElements = node.querySelectorAll && node.querySelectorAll('.ce-toolbar, .ce-toolbar__plus, .ce-toolbar__settings-btn, .ce-toolbar__content, .ce-toolbar__actions');
                        if (toolbarElements) {
                            toolbarElements.forEach(el => el.remove());
                        }
                    }
                });
            });
        });

        // Observer les changements dans tout le document pour être sûr
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // CSS minimal pour ajuster l'espacement
        const style = document.createElement('style');
        style.textContent = `
            .codex-editor__redactor {
                padding-left: 0 !important;
                margin-left: 0 !important;
            }
        `;
        document.head.appendChild(style);

        // Stocker l'observer pour le nettoyage
        this.toolbarObserver = observer;
    }

    /**
     * Setup slash commands functionality
     */
    setupSlashCommands() {
        if (!this.editor) return;

        // Create slash command suggestions
        const slashCommands = [
            { title: 'Titre', description: 'Titre H1, H2, H3...', icon: '📝', tool: 'header' },
            { title: 'Liste', description: 'Liste à puces ou numérotée', icon: '📋', tool: 'list' },
            { title: 'Liste de tâches', description: 'Liste avec cases à cocher', icon: '✅', tool: 'checklist' },
            { title: 'Citation', description: 'Bloc de citation', icon: '💬', tool: 'quote' },
            { title: 'Code', description: 'Bloc de code', icon: '💻', tool: 'code' },
            { title: 'Tableau', description: 'Insérer un tableau', icon: '📊', tool: 'table' },
            { title: 'Avertissement', description: 'Bloc d\'avertissement', icon: '⚠️', tool: 'warning' },
            { title: 'Image', description: 'Insérer une image', icon: '🖼️', tool: 'image' },
            { title: 'Vidéo/Embed', description: 'Intégrer une vidéo', icon: '🎥', tool: 'embed' },
            { title: 'Séparateur', description: 'Ligne de séparation', icon: '➖', tool: 'delimiter' },
            { title: 'HTML', description: 'Code HTML brut', icon: '🔧', tool: 'raw' },
            { title: 'Lien', description: 'Insérer un lien', icon: '🔗', tool: 'linkTool' }
        ];

        // Listen for input events only on editor container
        const editorElement = document.getElementById(this.holderId);
        if (editorElement) {
            editorElement.addEventListener('keydown', (event) => {
                this.handleSlashInput(event, slashCommands);
            });

            editorElement.addEventListener('input', (event) => {
                if (event.target.closest('.ce-paragraph')) {
                    this.detectSlashCommand(event, slashCommands);
                }
            });
        }
    }

    /**
     * Handle slash input
     */
    handleSlashInput(event, slashCommands) {
        // Handle Escape to close any open slash menu
        if (event.key === 'Escape') {
            this.closeSlashMenu();
            return;
        }

        // Handle Enter or Tab to select command
        if ((event.key === 'Enter' || event.key === 'Tab') && this.slashMenuOpen) {
            event.preventDefault();
            this.selectSlashCommand();
            return;
        }

        // Handle arrow keys for navigation
        if (this.slashMenuOpen && (event.key === 'ArrowUp' || event.key === 'ArrowDown')) {
            event.preventDefault();
            this.navigateSlashMenu(event.key === 'ArrowDown' ? 1 : -1);
            return;
        }
    }

    /**
     * Detect slash command in text
     */
    detectSlashCommand(event, slashCommands) {
        const target = event.target;
        const text = target.textContent || '';

        // Check if user typed "/" at the beginning of a line or after space
        if (text.match(/^\/\w*$/) || text.match(/\s\/\w*$/)) {
            const match = text.match(/\/(\w*)$/);
            if (match) {
                this.showSlashMenu(target, match[1], slashCommands);
            }
        } else {
            this.closeSlashMenu();
        }
    }

    /**
     * Show slash command menu
     */
    showSlashMenu(target, query, slashCommands) {
        // Remove existing menu
        this.closeSlashMenu();

        // Filter commands based on query
        const filteredCommands = slashCommands.filter(cmd =>
            cmd.title.toLowerCase().includes(query.toLowerCase()) ||
            cmd.description.toLowerCase().includes(query.toLowerCase())
        );

        if (filteredCommands.length === 0) return;

        // Create menu
        const menu = document.createElement('div');
        menu.className = 'slash-command-menu';
        menu.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #e8e8e8;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 8px 0;
            min-width: 350px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        `;

        filteredCommands.forEach((cmd, index) => {
            const item = document.createElement('div');
            item.className = 'slash-command-item';
            item.dataset.tool = cmd.tool;
            item.style.cssText = `
                padding: 12px 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: background-color 0.1s;
                ${index === 0 ? 'background-color: #f8f9fa;' : ''}
            `;

            item.innerHTML = `
                <span style="font-size: 16px;">${cmd.icon}</span>
                <div>
                    <div style="font-weight: 500; color: #1a1a1a;">${cmd.title}</div>
                    <div style="font-size: 12px; color: #666;">${cmd.description}</div>
                </div>
            `;

            item.addEventListener('mouseenter', () => {
                document.querySelectorAll('.slash-command-item').forEach(i =>
                    i.style.backgroundColor = ''
                );
                item.style.backgroundColor = '#f8f9fa';
                this.selectedSlashIndex = index;
            });

            item.addEventListener('click', () => {
                this.executeSlashCommand(cmd.tool, target);
            });

            menu.appendChild(item);
        });

        // Position menu
        const rect = target.getBoundingClientRect();
        menu.style.left = rect.left + 'px';
        menu.style.top = (rect.bottom + 5) + 'px';

        document.body.appendChild(menu);
        this.slashMenuElement = menu;
        this.slashMenuOpen = true;
        this.selectedSlashIndex = 0;
        this.slashTarget = target;
        this.filteredSlashCommands = filteredCommands;
    }

    /**
     * Close slash menu
     */
    closeSlashMenu() {
        if (this.slashMenuElement) {
            this.slashMenuElement.remove();
            this.slashMenuElement = null;
        }
        this.slashMenuOpen = false;
        this.selectedSlashIndex = -1;
        this.slashTarget = null;
        this.filteredSlashCommands = [];
    }

    /**
     * Navigate slash menu with arrow keys
     */
    navigateSlashMenu(direction) {
        if (!this.slashMenuElement || !this.filteredSlashCommands.length) return;

        this.selectedSlashIndex = Math.max(0, Math.min(
            this.filteredSlashCommands.length - 1,
            this.selectedSlashIndex + direction
        ));

        // Update visual selection
        const items = this.slashMenuElement.querySelectorAll('.slash-command-item');
        items.forEach((item, index) => {
            item.style.backgroundColor = index === this.selectedSlashIndex ? '#f8f9fa' : '';
        });
    }

    /**
     * Select current slash command
     */
    selectSlashCommand() {
        if (!this.filteredSlashCommands.length || this.selectedSlashIndex < 0) return;

        const selectedCommand = this.filteredSlashCommands[this.selectedSlashIndex];
        this.executeSlashCommand(selectedCommand.tool, this.slashTarget);
    }

    /**
     * Execute slash command
     */
    async executeSlashCommand(toolName, target) {
        this.closeSlashMenu();

        if (!this.editor) return;

        try {
            // Get current block index
            const currentBlockIndex = this.editor.blocks.getCurrentBlockIndex();

            // Remove the slash command text
            if (target) {
                const text = target.textContent || '';
                const newText = text.replace(/\/\w*$/, '');
                target.textContent = newText;
            }

            // Insert new block with the selected tool
            const newBlock = await this.editor.blocks.insert(toolName, {}, {}, currentBlockIndex + 1);

            // Focus the new block
            this.editor.caret.setToBlock(currentBlockIndex + 1);

        } catch (error) {
            console.error('Error executing slash command:', error);
        }
    }
}

// Export for use in Alpine.js components
window.LinguifyEditor = LinguifyEditor;